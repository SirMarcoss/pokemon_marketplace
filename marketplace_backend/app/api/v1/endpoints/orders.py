from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.orders_sh import OrderCreate, OrderRead
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.checkout_service import CheckoutService

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
