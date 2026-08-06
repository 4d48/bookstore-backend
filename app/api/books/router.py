from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status

from app.api.books.schemas import BookCreate, BookResponse, BookUpdate

books: dict[UUID, BookResponse] = {}
test_book_uuid: UUID = UUID("a10224b2-eb7f-4804-886b-e5d784e50382")
books[test_book_uuid] = BookResponse(id=test_book_uuid, title="The Little Prince")


router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=list[BookResponse])
def read_books():
    return books.values()


@router.get("/{book_id}", response_model=BookResponse)
def read_book(book_id: UUID):
    book = books.get(book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    return book


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_in: BookCreate):
    new_book_dict = book_in.model_dump()
    new_book_dict["id"] = uuid4()

    new_book = BookResponse.model_validate(new_book_dict)

    books[new_book.id] = new_book
    return new_book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(book_id: UUID, book_in: BookUpdate):
    stored_book = books.get(book_id)
    if stored_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    update_data = book_in.model_dump(exclude_unset=True)

    updated_book = stored_book.model_copy(update=update_data)

    books[updated_book.id] = updated_book

    return updated_book


@router.delete("/{book_id}", response_model=BookResponse)
def delete_book(book_id: UUID):
    if books.get(book_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    return books.pop(book_id)
