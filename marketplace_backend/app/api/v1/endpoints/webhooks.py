import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.services.payment_service import PaymentService

router = APIRouter()


@router.post("/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(None, alias="stripe-signature"),
    db: AsyncSession = Depends(get_db)
):
    """
    Riceve le notifiche asincrone da Stripe e valida la firma crittografica.
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header stripe-signature mancante"
        )

    # 1. Legge il corpo grezzo (RAW bytes)
    payload = await request.body()

    # 2. Verifica crittografica della firma con Stripe SDK
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Firma webhook non valida: {str(e)}")

    # 3. Smistamento dell'evento:
    # Se event["type"] == "payment_intent.succeeded":
    #    payment_intent = event["data"]["object"]
    #    payment_service = PaymentService(db)
    #    await payment_service.handle_successful_payment(payment_intent)

    # 4. Restituisci sempre 200 OK a Stripe per confermare la ricezione
        # return {"status": "success"}
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        payment_service = PaymentService(db)
        await payment_service.handle_successful_payment(payment_intent)
        return {"status": "success"}


    # composition of event
    # {
    #   "id": "evt_001",                   <-- BUSTA: ID della notifica
    #   "type": "payment_intent.succeeded", <-- BUSTA: Che tipo di evento è successo?
    #   "created": 1700000000,              <-- BUSTA: A che ora è successo?
    #
    #   "data": {                           <-- CONTENUTO DELLA BUSTA
    #
    #     "object": {                       <-- IL FOGLIO REALE (L'oggetto PaymentIntent di Stripe!)
    #       "id": "pi_3MtwBwLkdIwHu7ix",
    #       "amount": 5000,
    #       "currency": "eur",
    #       "status": "succeeded",
    #       "metadata": {                   <-- I TUOI METADATA SI TROVANO QUI DENTRO!
    #         "order_id": "8f3b2a1c-...",
    #         "customer_email": "mario@rossi.it"
    #       }
    #     }
    #
    #   }
    # }

    # Stripe gestisce centinaia di eventi diversi:
    #
    # Se un cliente cancella l'abbonamento
    # →
    # → type: "customer.subscription.deleted", e dentro event["data"]["object"] ci sarà l'oggetto Subscription.
    # Se fai un rimborso
    # →
    # → type: "charge.refunded", e dentro event["data"]["object"] ci sarà l'oggetto Refund.
    # Se il pagamento è confermato
    # →
    # → type: "payment_intent.succeeded", e dentro event["data"]["object"] c'è l'oggetto PaymentIntent.