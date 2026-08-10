from decimal import Decimal

from pydantic import BaseModel


class BookBase(BaseModel):
    title: str
    isbn: str | None = None
    price: Decimal | None = None
    currency: str | None = None


# Response
class BookResponse(BookBase):
    id: int


# Request
class BookCreate(BookBase):
    pass


# Request
class BookUpdate(BaseModel):
    title: str | None = None
    isbn: str | None = None
    price: Decimal | None = None
    currency: str | None = None
