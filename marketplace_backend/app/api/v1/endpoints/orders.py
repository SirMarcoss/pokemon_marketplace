from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.orders_sh import OrderCreate, OrderRead
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.checkout_service import CheckoutService
from app.services.payment_service import PaymentService
from app.schemas.orders_sh import PaymentIntentResponse
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





