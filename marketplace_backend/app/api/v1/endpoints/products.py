from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.products_sh import ProductRead, ProductDetailRead, ProductCreate
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.product_variants_sh import ProductVariantRead, ProductVariantCreate



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

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non hai i permessi per creare prodotti nel catalogo."
        )

    product_service = ProductService(db)


    return await product_service.create_product(product_in)



@router.post(
    "/variants",
    response_model=ProductVariantRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)]  # Il buttafuori a livello di rotta
)
async def create_variant(
        variant_in: ProductVariantCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Aggiunge una nuova variante (stock, prezzo, condizione) a un prodotto esistente.
    """

    product_service = ProductService(db)
    try:
        result = await product_service.create_product_variant(variant_in)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
