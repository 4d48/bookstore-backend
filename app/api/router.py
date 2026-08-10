from fastapi import APIRouter

from app.api.authors.router import router as authors_router
from app.api.books.router import router as books_router

router = APIRouter(prefix="/api")
router.include_router(books_router)
router.include_router(authors_router)
