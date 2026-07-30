from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.products_sh import ProductRead, ProductDetailRead
from app.schemas.product_variants_sh import ProductVariantRead
from app.schemas.products_sh import ProductCreate
from app.core.security import get_current_user  # Oppure dal file in cui l'hai salvata
from app.models.user import User  # Il tuo modello utente



router = APIRouter()


@router.get("/", response_model=list[ProductRead])
async def list_products(
    skip: int = Query(0, ge=0, description="Quanti prodotti saltare"),
    limit: int = Query(50, ge=1, le=100, description="Massimo 100 prodotti per pagina"),
    db: AsyncSession = Depends(get_db)
):
    """
    Recupera il catalogo dei prodotti impaginato.
    """

    product_service = ProductService(db)
    try:
        result = await product_service.get_products(skip, limit)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{slug}", response_model=ProductDetailRead)
async def get_product(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Recupera i dettagli di un singolo prodotto, incluse le sue varianti, tramite lo slug.
    """
    product_service = ProductService(db)
    product_data = await product_service.get_product_by_slug(slug)
    if product_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return product_data


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
        product_in: ProductCreate,  # Il payload JSON in ingresso
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)  # IL BUTTAFUORI
):
    """
    Crea un nuovo prodotto. Accessibile solo agli utenti autenticati.
    """
    # Se il token manca o è falso, FastAPI blocca la richiesta prima di arrivare qui.

    product_service = ProductService(db)

    # In futuro, potremmo aggiungere un controllo: if not current_user.is_admin: raise 403

    return await product_service.create_product(product_in)

