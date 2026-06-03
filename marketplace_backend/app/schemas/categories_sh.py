from pydantic.main import BaseModel
from pydantic.config import ConfigDict
from pydantic.fields import Field
from typing import Optional


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None


    model_config = ConfigDict(from_attributes=True)
    # By default, Pydantic only knows how to read dictionaries.
    # When FastAPI returns data from the DB, it passes a SQLAlchemy object, not a dict.
    # SQLAlchemy objects expose data as attributes (obj.id, obj.name),
    # not as dictionary keys (obj["id"], obj["name"]).
    # from_attributes=True tells Pydantic to read attributes instead of dictionary keys,
    # allowing it to convert a SQLAlchemy object directly into this response schema.