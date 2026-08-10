from pydantic import BaseModel

from app.api.books.schemas import BookResponse


class AuthorBase(BaseModel):
    name: str


class AuthorResponse(AuthorBase):
    id: int


class AuthorBooksResponse(BaseModel):
    books: list[BookResponse]


class AuthorCreate(AuthorBase):
    book_ids: list[int] = []
