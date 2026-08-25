from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.orders_sh import OrderCreate, OrderRead
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.checkout_service import CheckoutService
from app.services.payment_service import PaymentService
from app.services.order_service import OrderService
from app.schemas.orders_sh import PaymentIntentResponse, OrderDetailRead
from uuid import UUID

router = APIRouter()

@router.post("/checkout", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def process_checkout_endpoint(
        order_in: OrderCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Trasforma il carrello dell'utente in un Ordine.
    """
    checkout_service = CheckoutService(db)
    try:
        result = await checkout_service.process_checkout(current_user.id, order_in)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{order_id}/create-payment-intent",
    response_model=PaymentIntentResponse,
    status_code=status.HTTP_200_OK
)
async def create_payment_intent_endpoint(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Genera un PaymentIntent su Stripe per un ordine esistente in stato PENDING.
    Restituisce il client_secret necessario al frontend per renderizzare Stripe Elements.
    """
    payment_service = PaymentService(db)
    try:
        result = await payment_service.create_payment_intent_for_order(order_id, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/me",
    response_model=list[OrderDetailRead],  # lista di ordini
    status_code=status.HTTP_200_OK
)
async def get_my_orders(
        skip: int = Query(default=0, ge=0), # per Query guarda note --> validazione quantità di dati
        limit: int = Query(default=20, ge=1, le=50),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Restituisce la lista degli ordini dell'utente connesso.
    """
    order_service = OrderService(db)
    result = await order_service.get_user_orders(current_user.id, skip, limit)
    return result
#


@router.get("/{order_id}",
            response_model=OrderDetailRead,
            status_code=status.HTTP_200_OK
)
async def get_order_detail(
        order_id : UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Restituisce il dettaglio di un singolo ordine dell'utente.
    """
    order_service = OrderService(db)
    order = await order_service.get_order_by_id(order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ordine non trovato")
    return order

# /{order_id} Le parentesi graffe dicono a FastAPI: "Questa parte dell'URL non è fissa,
# ma è una variabile che cambia a ogni richiesta
# /me è la convenzione REST universale per dire: "Dammi le risorse appartenenti all'utente attualmente autenticato".












