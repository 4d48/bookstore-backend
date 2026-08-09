from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class BookBase(BaseModel):
    title: str
    isbn: str | None = None
    price: Decimal | None = None
    currency: str | None = None


# Request
class BookCreate(BookBase):
    pass


# Response
class BookResponse(BookBase):
    id: int


# Request
class BookUpdate(BaseModel):
    title: str | None = None
    isbn: str | None = None
    price: Decimal | None = None
    currency: str | None = None
