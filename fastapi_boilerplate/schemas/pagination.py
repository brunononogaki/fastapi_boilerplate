from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

# Generic type for the data items
T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response schema
    """

    items: List[T] = Field(..., description='List of items for current page')
    total_count: int = Field(..., description='Total number of items available')
    page: int = Field(..., description='Current page number (calculated from skip/limit)')
    page_size: int = Field(..., description='Number of items per page')
    total_pages: int = Field(..., description='Total number of pages')
    has_next: bool = Field(..., description='Whether there are more pages')
    has_previous: bool = Field(..., description='Whether there are previous pages')


class FilterPage(BaseModel):
    skip: int = Field(ge=0)
    limit: int = Field(ge=1, le=200)
