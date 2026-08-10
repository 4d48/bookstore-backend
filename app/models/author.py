from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.associations import books_to_authors

if TYPE_CHECKING:
    from app.models.book import Book


class Author(Base):
    __tablename__: str = "authors"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    books: Mapped[list["Book"]] = relationship(
        secondary=books_to_authors, back_populates="authors"
    )
