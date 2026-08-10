# Used for:
# 1. generating SQLAlchemy metadata (main purpose)
# 2. importing all ORM models at once


from app.database import Base
from app.models.associations import books_to_authors
from app.models.author import Author
from app.models.book import Book

__all__ = ["Author", "Base", "Book", "books_to_authors"]
