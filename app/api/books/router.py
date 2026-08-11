from fastapi import APIRouter, HTTPException, status
from sqlalchemy import delete, select

from app.api.books.schemas import BookCreate, BookResponse, BookUpdate
from app.database import SessionDep
from app.models import Book

router = APIRouter(prefix="/books", tags=["books"])


@router.get("", response_model=list[BookResponse])
async def read_books(db: SessionDep):
    result = await db.scalars(select(Book))

    return result.all()


@router.get("/{book_id}", response_model=BookResponse)
async def read_book(db: SessionDep, book_id: int):
    book = await db.get(Book, book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    return book


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(db: SessionDep, book_in: BookCreate):
    book = Book(**book_in.model_dump())

    async with db.begin():
        db.add(book)

    return book


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(db: SessionDep, book_id: int, book_in: BookUpdate):
    async with db.begin():
        stored_book = await db.get(Book, book_id)

        if stored_book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )

        update_data = book_in.model_dump()

        for key, value in update_data.items():  # pyright: ignore[reportAny]
            setattr(stored_book, key, value)

    return stored_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(db: SessionDep, book_id: int):
    async with db.begin():
        stmt = delete(Book).where(Book.id == book_id)

        result = await db.execute(stmt)

        if result.rowcount == 0:  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Book not found")
