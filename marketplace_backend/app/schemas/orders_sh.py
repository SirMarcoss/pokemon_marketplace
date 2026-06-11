from pydantic.main import BaseModel
from pydantic.config import ConfigDict
from pydantic.types import EmailStr
from pydantic.fields import Field
from app.models.orders import  FulfillmentStatusEnum, PaymentStatusEnum
from uuid import UUID
from datetime import datetime


class Address(BaseModel):
    street: str = Field(..., min_length=1, max_length=255)
    number: str = Field(..., max_length=10)
    city: str = Field(..., min_length=1, max_length=100)
    province: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., pattern=r'^\d{5}$')  # Italian format
    country: str = Field(default="Italy", max_length=100)
    company_name: str | None = None
    tax_id: str | None = None  # Partita IVA


class OrderCreate(BaseModel):
    customer_email: EmailStr = Field(..., max_length=255, description="Email of the customer placing the order")
    shipping_address : Address
    billing_address : Address
    notes: str | None = Field(None, max_length=1000, description="Optional notes for the order, max length 1000 characters")


class OrderAdminUpdate(BaseModel):
    payment_status: PaymentStatusEnum | None = Field(None, description="Updated payment status for the order")
    fulfillment_status: FulfillmentStatusEnum | None = Field(None, description="Updated fulfillment status for the order")
    notes: str | None = Field(None, max_length=1000, description="Optional notes for the order, max length 1000 characters")


class OrderRead(BaseModel):
    id: UUID
    user_id: UUID | None
    customer_email: EmailStr = Field(..., max_length=255)
    shipping_address: Address
    billing_address: Address
    total_amount_cents: int
    stripe_intent_id: str | None = Field(None, max_length=255)
    payment_status: PaymentStatusEnum
    fulfillment_status: FulfillmentStatusEnum
    notes: str | None = Field(None, max_length=1000)
    created_at: datetime
    updated_at: datetime


    model_config = ConfigDict(from_attributes=True)