from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.cart_items_sh import CartItemBaseCreate, CartItemBaseRead
from app.services.cart_service import CartService

router = APIRouter()

@router.post("/", response_model=CartItemBaseRead, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    item_in: CartItemBaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # IL BUTTAFUORI CI CONSEGNA L'UTENTE!
):
    """
    Aggiunge una variante (carta) al carrello dell'utente loggato.
    Se il carrello non esiste, viene creato in automatico.
    """
    # 1. Istanzia il CartService passando la sessione del database (db)
    cart_service = CartService(db)

    try:
        result = await cart_service.add_item_to_cart(current_user.id, item_in)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))

