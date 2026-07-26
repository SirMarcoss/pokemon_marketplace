from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.products import Product
from app.models.product_variants import ProductVariant



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