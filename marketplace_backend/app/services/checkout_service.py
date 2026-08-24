from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from decimal import Decimal

from app.models import ProductVariant, Product
from app.models.orders import Order
from app.models.order_items import OrderItem
from app.models.carts import Cart
from app.models.cart_items import CartItem
from app.schemas.orders_sh import OrderCreate


class CheckoutService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_checkout(self, user_id: UUID, order_in: OrderCreate) -> Order:
        """
        Esegue il checkout del carrello trasformandolo in un ordine tramite Transazione ACID.
        """
        # 1. RECUPERO IL CARRELLO E TUTTE LE SUE RELAZIONI
        stmt = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.items).selectinload(CartItem.variant)
                     .selectinload(ProductVariant.product))
        )
        result = await self.db.execute(stmt)
        cart = result.scalar_one_or_none()

        # Fail-Fast: Se il carrello non c'è o è vuoto
        if not cart or not cart.items:
            raise ValueError("Il carrello è vuoto o inesistente.")

        # INIZIO DELLA TRANSAZIONE
        try:
            total_cents = 0

            # 2. CREAZIONE DELL'ORDINE (Usando il modello SQLAlchemy 'Order')
            new_order = Order(
                user_id=user_id,
                customer_email=order_in.customer_email,
                # Convertiamo l'oggetto Pydantic in un dict Python compatibile con JSONB
                shipping_address=order_in.shipping_address.model_dump(),
                billing_address=order_in.billing_address.model_dump(),
                notes=order_in.notes,
                total_amount_cents=0  # Lo aggiorniamo alla fine del calcolo
            )

            self.db.add(new_order)
            await self.db.flush()  # Genera l'ID dell'ordine senza chiudere la transazione

            # 3. CICLO SUGLI ITEMS DEL CARRELLO
            for cart_item in cart.items:
                variant = cart_item.variant

                # a) Controllo Stock
                if variant.stock < cart_item.quantity:
                    raise ValueError(f"Quantità non disponibile per l'articolo {variant.sku}")

                # b) Sottrazione dello stock fisico
                variant.stock -= cart_item.quantity
                unit_price = variant.price_gross_cents

                line_total = variant.price_gross_cents * cart_item.quantity
                total_cents += line_total

                # d) Creazione dello "Scontrino" (OrderItem)
                order_item = OrderItem(
                    order_id=new_order.id,
                    variant_id=variant.id,
                    quantity=cart_item.quantity,

                    # Congeliamo i dati storici
                    product_name_at_purchase=variant.product.title,  # Modifica se il nome è in un'altra tabella
                    sku_at_purchase=variant.sku,
                    price_net_cents_at_purchase=variant.price_net_cents,
                    tax_rate_at_purchase=variant.tax_rate,
                    price_gross_cents_at_purchase=variant.price_gross_cents
                )
                self.db.add(order_item)

            # 4. AGGIORNO IL TOTALE E PULISCO IL CARRELLO
            new_order.total_amount_cents = total_cents
            await self.db.delete(cart)  # Distruggo il carrello

            # 5. COMMIT FINALE
            await self.db.commit()

            # Ricarichiamo l'ordine con i suoi items freschi di database per restituirlo
            await self.db.refresh(new_order, ["items"])
            return new_order

        except Exception as e:
            # ROLLBACK: In caso di errore (es. stock insufficiente), annulla tutte le modifiche
            await self.db.rollback()
            raise ValueError(f"Checkout fallito: {str(e)}")