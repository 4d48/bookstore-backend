from fastapi import APIRouter, HTTPException, status
from sqlalchemy import delete, insert, select

from app.api.authors.schemas import (
    AuthorBooksResponse,
    AuthorCreate,
    AuthorCreateResponse,
    AuthorResponse,
)
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
async def get_books_by_author(db: SessionDep, author_id: int):
    async with db.begin():
        # SELECT books.id
        # FROM books
        # JOIN books_to_authors ON books.id = books_to_authors.book_id
        # WHERE books_to_authors.author_id = author_id;
        stmt = select(Book).join(Book.authors).where(Author.id == author_id)

        result = await db.scalars(stmt)

        books = result.all()

    if not books:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Author not found")

    return {"books": books}


@router.post(
    "", response_model=AuthorCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_author(db: SessionDep, author_in: AuthorCreate):
    async with db.begin():
        found_ids: set[int] = set()

        if author_in.book_ids:
            unique_book_ids = set(author_in.book_ids)

            stmt = select(Book.id).where(Book.id.in_(author_in.book_ids))

            result = await db.scalars(stmt)

            found_ids = set(result.all())
            missing_ids = unique_book_ids - found_ids

            if missing_ids:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND,
                    detail=f"Books with IDs {missing_ids} not found",
                )

        author = Author(name=author_in.name)
        db.add(author)
        await db.flush()  # get author.id

        if found_ids:
            insert_values = [
                {"book_id": book_id, "author_id": author.id} for book_id in found_ids
            ]

            _ = await db.execute(insert(books_to_authors), insert_values)

    return AuthorCreateResponse(
        id=author.id, name=author.name, book_ids=author_in.book_ids
    )


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(db: SessionDep, author_id: int):
    async with db.begin():
        stmt = delete(Author).where(Author.id == author_id)

        result = await db.execute(stmt)

        if result.rowcount == 0:  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Author not found")
