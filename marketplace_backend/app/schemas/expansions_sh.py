from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.config import ConfigDict
from datetime import date
from typing import Optional


class ExpansionCreate(BaseModel):
    category_id: int
    name: str = Field(..., min_length=1, max_length=255)
    release_date: Optional[date] = None
    total_cards: Optional[int] = Field(None, ge=0)


class ExpansionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    release_date: Optional[date] = None
    total_cards: Optional[int] = Field (None, ge=0)
    

class ExpansionRead(BaseModel):
    id: int
    category_id: int
    name: str
    release_date: Optional[date] = None
    total_cards: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
