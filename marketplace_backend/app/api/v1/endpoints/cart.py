from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.cart_items_sh import CartItemBaseCreate, CartItemBaseRead, CartItemBaseUpdate
from app.services.cart_service import CartService
from uuid import  UUID

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


@router.get("/", response_model=CartItemBaseRead, status_code=status.HTTP_200_OK)
async def get_my_cart(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Restituisce il carrello dell'utente loggato con i dettagli completi delle carte.
    """
    cart_service = CartService(db)
    result = await cart_service.get_cart_with_details(current_user.id)
    return result
    # nessun uso di try/exept perchè il metodo get_cart_with_details non solleva mai un errore, se non trova
    # il carrello ne crea uno vuoto


@router.put("/items/{item_id}", status_code=status.HTTP_200_OK)
async def update_item_quantity(
    item_id: UUID,
    item_in: CartItemBaseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Aggiorna la quantità di un prodotto nel carrello.
    """
    cart_service = CartService(db)
    try:
        result = await cart_service.update_cart_item(current_user.id, item_id, item_in.quantity)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_cart(
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Rimuove un prodotto dal carrello.
    """
    cart_service = CartService(db)
    try:
        await cart_service.remove_cart_item(current_user.id, item_id)
        # Non serve alcun return. FastAPI tradurrà il termine
        # della funzione in una risposta vuota con status 204.
    except ValueError as e:
        # Trasformiamo l'errore del service in un 404 (non trovato)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


