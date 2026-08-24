from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.products import Product
from app.models.product_variants import ProductVariant
from app.schemas.product_variants_sh import ProductVariantCreate
from slugify import slugify
from app.schemas.products_sh import ProductCreate


class ProductService:
    """
    Gestisce la logica di business per il catalogo dei prodotti (carte, espansioni).
    """

    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_products(self, skip: int = 0, limit: int = 50) -> list[Product]:
        """
        Recupera una lista paginata di prodotti.
        """
        stmt = select(Product).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()


    async def get_product_by_slug(self, slug: str) -> dict | None:
        # 1. Trova il prodotto
        stmt_product = select(Product).where(Product.slug == slug)
        product_result = await self.db.execute(stmt_product)
        product = product_result.scalar_one_or_none()
        # scalar_one_or_none() estrae l'unico risultato atteso.
        # Se la carta non esiste, restituisce None in automatico.

        if not product:
            return None

        # 2. Trova le varianti associate (es. ProductVariant.product_id == product.id)
        stmt_variants = select(ProductVariant).where(ProductVariant.product_id == product.id)
        variants_result = await self.db.execute(stmt_variants)
        variants = variants_result.scalars().all()

        # Restituisce un dizionario o un oggetto DTO che aggrega i dati
        return {
            "product": product,
            "variants": variants
        }


    async def create_product(self, product_in: ProductCreate) -> Product:
        """
        Crea un nuovo prodotto nel database generando automaticamente lo slug.
        """
        # 1. Genera lo slug a partire dal titolo (product_in.title) usando la funzione slugify()
        generated_slug = slugify(product_in.title)
        product_data = product_in.model_dump()

        db_product = Product(**product_data, slug=generated_slug)

        self.db.add(db_product)
        await self.db.commit()
        await self.db.refresh(db_product)

        return db_product


    async def create_product_variant(self, variant_in: ProductVariantCreate) -> ProductVariant:
        """
        Crea una nuova variante (es. Foil, First Edition) collegandola a un prodotto esistente.
        """
        stmt_product_variant = select(Product).where(Product.id == variant_in.product_id)
        result = await self.db.execute(stmt_product_variant)
        product_variant = result.scalar_one_or_none()

        if not product_variant:
            raise ValueError(f"Prodotto con ID {variant_in.product_id} non trovato.")

        # 1. Smonta l'oggetto Pydantic in un dizionario
        variant_data = variant_in.model_dump()

        # 2. Spacchettalo direttamente dentro il modello SQLAlchemy!
        db_product_variant = ProductVariant(**variant_data)

        self.db.add(db_product_variant)
        await self.db.commit()
        await self.db.refresh(db_product_variant)

        return db_product_variant