from decimal import Decimal

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


class Book(Base):
    __tablename__: str = "books"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    isbn: Mapped[str] = mapped_column(String(20), nullable=True, unique=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=True)

    authors: Mapped[list["Author"]] = relationship(
        secondary=books_to_authors, back_populates="books"
    )


class Author(Base):
    __tablename__: str = "authors"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    books: Mapped[list["Book"]] = relationship(
        secondary=books_to_authors, back_populates="authors"
    )
