# Used for:
# 1. generating SQLAlchemy metadata (main purpose)
# 2. importing all ORM models at once

from app.api.books.models import Author, Book
from app.database import Base

__all__ = ["Author", "Base", "Book"]
