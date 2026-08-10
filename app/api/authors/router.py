from fastapi import APIRouter, HTTPException, status
from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload

from app.api.authors.schemas import AuthorBooksResponse, AuthorCreate, AuthorResponse
from app.database import SessionDep
from app.models import Author, Book
from app.models.associations import books_to_authors

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("", response_model=list[AuthorResponse])
async def get_authors(db: SessionDep):
    async with db.begin():
        result = await db.scalars(select(Author))
        authors = result.all()

    return authors


@router.get("/{author_id}", response_model=AuthorResponse)
async def get_author(db: SessionDep, author_id: int):
    async with db.begin():
        author = await db.get(Author, author_id)

    if author is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Author not found")

    return author


@router.get("/{author_id}/books", response_model=AuthorBooksResponse)
async def get_author_books(db: SessionDep, author_id: int):
    async with db.begin():
        stmt = (
            select(Author)
            .where(Author.id == author_id)
            .options(selectinload(Author.books))
        )

        author = await db.scalar(stmt)

    if author is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Author not found")

    return author


@router.post("", response_model=AuthorResponse)
async def create_author(db: SessionDep, author_in: AuthorCreate):
    async with db.begin():
        unique_book_ids = set(author_in.book_ids)
        stmt = select(Book.id).where(Book.id.in_(author_in.book_ids))

        result = await db.scalars(stmt)

        books_found = result.all()

        if len(books_found) < len(unique_book_ids):
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Some books were not found",  # todo: tell exactly what books were not found
            )

        author = Author(name=author_in.name)
        db.add(author)
        await db.flush()

        insert_values = [
            {"book_id": book_id, "author_id": author.id} for book_id in books_found
        ]

        _ = await db.execute(insert(books_to_authors), insert_values)

    return author


@router.delete("/{author_id}", response_model=AuthorResponse)
async def delete_author(db: SessionDep, author_id: int):
    async with db.begin():
        author = await db.get(Author, author_id)

        if author is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Author not found")

        await db.delete(author)

    return author
