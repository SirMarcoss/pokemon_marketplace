from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.models.carts import Cart
from app.models.cart_items import CartItem
from app.models.product_variants import ProductVariant
from app.schemas.cart_items_sh import CartItemBaseCreate
from uuid import UUID
import uuid


class CartService:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_or_create_cart(self, user_id: uuid.UUID) -> Cart:
        """
        Cerca il carrello dell'utente loggato. Se non esiste, lo crea.
        Per ora ignoriamo la logica 'Guest' (session_id) per semplicità.
        """
        stmt = select(Cart).where(Cart.user_id == user_id)
        result = await self.db.execute(stmt)
        if result:
            return result.scalar().all()
        else:
            new_cart = Cart(user_id=user_id)

            # Aggiungiamo l'oggetto alla sessione e salviamo su disco
            self.db.add(new_cart)
            await self.db.commit()
            # Aggiorniamo l'oggetto per farci restituire l'ID generato dal DB
            await self.db.refresh(new_cart)

            return new_cart


    async def add_item_to_cart(self, user_id: uuid.UUID, item_in: CartItemBaseCreate) -> CartItem:
        """
        Aggiunge una variante al carrello dell'utente o ne aggiorna la quantità.
        """
        # --- FASE 1: RECUPERO CONTENITORE ---
        # Richiamiamo un altro metodo della classe per garantirci che l'utente abbia un carrello.
        # Se non lo ha, questa funzione glielo crea "silenziosamente" in background.
        cart = await self.get_or_create_cart(user_id)

        # --- FASE 2: VALIDAZIONE PRODOTTO E STOCK BASE ---
        # Interroghiamo il DB per cercare la variante esatta richiesta.
        stmt_variant = select(ProductVariant).where(ProductVariant.id == item_in.variant_id)
        result = await self.db.execute(stmt_variant)
        variant = result.scalar_one_or_none()

        # CRITICO: Regola di business 1 (Fail Fast). Se il prodotto non esiste, blocca tutto.
        if not variant:
            raise ValueError("Variante non trovata")

        # CRITICO: Regola di business 2. Se l'utente chiede 5 carte, ma in magazzino ce ne sono 3,
        # blocchiamo subito l'operazione per evitare inconsistenze.
        if variant.stock < item_in.quantity:
            raise ValueError(f"Stock insufficiente. Disponibili: {variant.stock}, Richiesti: {item_in.quantity}")

        # --- FASE 3: RICERCA NEL CARRELLO ---
        # Verifichiamo se QUESTA variante è già dentro QUESTO carrello.
        # Usiamo l'operatore AND (implicito passando due argomenti al where).
        stmt_existing = select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.variant_id == item_in.variant_id
        )
        result_existing = await self.db.execute(stmt_existing)
        existing_item = result_existing.scalar_one_or_none()

        # --- FASE 4: LOGICA BIVIO (AGGIORNA o CREA) ---
        if existing_item:
            # SCENARIO A: L'oggetto è già nel carrello.

            # Calcoliamo la somma tra quello che c'è già e quello che vuole aggiungere ora.
            nuova_quantita = existing_item.quantity + item_in.quantity

            # CRITICO: Regola di business 3. Magari in magazzino ci sono 5 carte.
            # L'utente ne aveva già 4 nel carrello e ora ne chiede altre 2 (totale 6).
            # Dobbiamo bloccarlo di nuovo!
            if variant.stock < nuova_quantita:
                raise ValueError(f"L'aggiunta supera lo stock. Hai già {existing_item.quantity} pezzi nel carrello.")

            # Modifichiamo l'istanza Python (in memoria).
            existing_item.quantity = nuova_quantita

            # CRITICO: Siccome l'oggetto existing_item è "tracciato" da SQLAlchemy,
            # basta fare commit per generare in automatico un UPDATE in linguaggio SQL.
            await self.db.commit()
            await self.db.refresh(existing_item)

            return existing_item

        else:
            # SCENARIO B: L'oggetto non è nel carrello. È un nuovo inserimento.

            # Istanziamo una nuova riga passando i riferimenti alle chiavi esterne (cart.id)
            new_cart_item = CartItem(
                cart_id=cart.id,
                variant_id=item_in.variant_id,
                quantity=item_in.quantity
            )

            # CRITICO: Siccome è un oggetto nuovo, SQLAlchemy non lo conosce.
            # Dobbiamo usare .add() per inserirlo nella transazione prima del commit (INSERT SQL).
            self.db.add(new_cart_item)
            await self.db.commit()

            # Recuperiamo l'oggetto dal DB per avere il suo nuovo 'id' (Primary Key) generato.
            await self.db.refresh(new_cart_item)

            return new_cart_item

    async def get_cart_with_details(self, user_id: uuid.UUID) -> Cart:
        """
        Recupera il carrello dell'utente con tutti gli items e le rispettive varianti (Eager Loading).
        """
        stmt = select(Cart).where(Cart.user_id == user_id).options(selectinload(Cart.items).selectinload(CartItem.variant))
        result = await self.db.execute(stmt)
        cart = result.scalar_one_or_none()
        if cart:
            return cart
        else:
            new_cart = await self.get_or_create_cart(user_id)
            return new_cart


    async def update_cart_item(self, user_id: UUID, item_id: UUID, quantity: int) -> CartItem:
        """
        Obiettivo: Trovare il CartItem, verificare che appartenga all'utente,
        controllare lo stock della variante associata e aggiornare la quantità.
        """
        stmt = select(Cart).where(Cart.user_id == user_id).options(selectinload(Cart.items).selectinload(CartItem.variant))
        result = await self.db.execute(stmt)
        cart = result.scalar_one_or_none()
        if not cart:
            raise ValueError("Carrello non trovato")

        target_item = None
        for item in cart.items:
            if item.id == item_id:
                target_item = item
                break

        if not target_item:
            raise ValueError("Prodotto non presente nel tuo carrello")

        # 3. Controlla lo stock usando la variante che hai pre-caricato
        if target_item.variant.stock < quantity:
            raise ValueError(f"Stock insufficiente. Massima disponibilità: {target_item.variant.stock}")

        # 4. Aggiorna la quantità (Python capisce che l'oggetto è stato modificato)
        target_item.quantity = quantity

        # 5. Sincronizza la RAM con il Database fisico
        await self.db.commit()

        return target_item


    async def remove_cart_item(self, user_id: UUID, item_id: UUID) -> None:
        # 1. Trova l'item da cancellare accertandoti che appartenga all'utente
        stmt = (
            select(CartItem)
            .join(Cart)  # Colleghiamo la tabella Cart
            .where(
                CartItem.id == item_id,
                Cart.user_id == user_id  # Ora il confronto è corretto!
            )
        )
        result = await self.db.execute(stmt)
        target_item = result.scalar_one_or_none()

        if not target_item:
            raise ValueError("Elemento non trovato nel tuo carrello")

        # 2. Passa l'oggetto fisico alla funzione delete
        await self.db.delete(target_item)

        # 3. Applica la distruzione nel database
        await self.db.commit()