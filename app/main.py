from decimal import Decimal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class Book(BaseModel):
    id: int
    title: str
    isbn: str | None = None
    price: Decimal | None = None
    currency: str | None = None


app = FastAPI()

books: list[Book] = []
books.append(Book(id=1, title="Little Prince"))


@app.get("/api/books")
def get_books():
    return books


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    return [book for book in books if book.id == book_id]


@app.post("/api/books")
def add_book(book: Book):
    for stored_book in books:
        if book.id == stored_book.id:
            raise HTTPException(
                status_code=400,
                detail="The book with this id already exists",
            )

    books.append(book)
    return book


@app.put("/api/books/{book_id}")
def update_book(book_id: int, new_book: Book):
    for index, book in enumerate(books):
        if book.id == book_id:
            books[index] = new_book
            return new_book

        raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/api/books/{book_id}")
def delete_book(book_id: int):
    for book in books:
        if book.id == book_id:
            books.remove(book)
            return book

    raise HTTPException(status_code=404, detail="Book not found")
