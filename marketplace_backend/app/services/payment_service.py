import stripe
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.orders import Order, PaymentStatusEnum


# 1. Configurazione globale della chiave segreta di Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment_intent_for_order(self, order_id: UUID, user_id: UUID) -> dict:
        """
        1. Recupera l'ordine dal DB verificando che appartenga a user_id.
        2. Verifica che l'ordine sia in stato payment_status == PaymentStatusEnum.PENDING.
        3. Se l'ordine ha già uno 'stripe_intent_id', recupera quello esistente da Stripe
           oppure ne crea uno nuovo chiamando 'stripe.PaymentIntent.create(...)'.
        4. Salva 'order.stripe_intent_id' nel DB e fa commit.
        5. Restituisce un dizionario contenente il 'client_secret' per il frontend.
        """
        stmt = select(Order).where(Order.id == order_id).where(Order.user_id == user_id)
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError("Ordine non trovato")
        if order.payment_status != PaymentStatusEnum.PENDING:
            raise ValueError("L'ordine non è in attesa di pagamento")
        if order.total_amount_cents <= 0:
            raise ValueError("Importo dell'ordine non valido")

        # C) Chiamata all'SDK di Stripe (stripe.PaymentIntent.create):
        intent = stripe.PaymentIntent.create(
            amount=order.total_amount_cents,
            currency="eur",
            metadata= {"order_id": str(order_id), "customer_email": order.customer_email}
        )

        # D) Aggiorna l'ordine:
        # order.stripe_intent_id = intent.id
        # await self.db.commit()
        order.stripe_intent_id = intent.id
        await self.db.commit()

        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id
        }


    async def handle_successful_payment(self, payment_intent: dict) -> Order:
        """
        Riceve l'oggetto PaymentIntent dal Webhook di Stripe,
        estrae l'order_id dai metadata e aggiorna lo stato dell'ordine a PAID.
        """

        # 1. Estrai 'order_id' da payment_intent.get("metadata", {}).get("order_id")
        # 2. Cerca l'ordine nel DB tramite UUID(order_id)
        # 3. Aggiorna lo stato:

        order_id = payment_intent.get("metadata", {}).get("order_id")
        if not order_id:
            raise ValueError("order_id mancante nei metadata")

        stmt = select(Order).where(Order.id == order_id)
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            raise ValueError(f"Ordine {order_id} non trovato")

        order.payment_status = PaymentStatusEnum.PAID
        await self.db.commit()
        return order