from sqlalchemy import Column, ForeignKey, Integer, Table

from app.database import Base

books_to_authors = Table(
    "books_to_authors",
    Base.metadata,
    Column(
        "book_id",
        Integer,
        ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "author_id",
        Integer,
        ForeignKey("authors.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)
