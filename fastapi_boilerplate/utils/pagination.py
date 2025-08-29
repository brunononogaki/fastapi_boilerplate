import math
from typing import List, TypeVar

from fastapi_boilerplate.schemas.pagination import PaginatedResponse

T = TypeVar('T')


def create_paginated_response(items: List[T], total_count: int, skip: int, limit: int) -> PaginatedResponse[T]:
    """
    Create a paginated response with all pagination metadata
    Args:
        items: List of items for current page
        total_count: Total number of items available
        skip: Number of items skipped
        limit: Number of items per page
    Returns:
        PaginatedResponse with pagination metadata
    """

    # Calculate current page (1-based)
    current_page = (skip // limit) + 1 if limit > 0 else 1

    # Calculate total pages
    total_pages = math.ceil(total_count / limit) if limit > 0 else 1

    # Calculate pagination flags
    has_next = current_page < total_pages
    has_previous = current_page > 1

    return PaginatedResponse(
        items=items,
        total_count=total_count,
        page=current_page,
        page_size=limit,
        total_pages=total_pages,
        has_next=has_next,
        has_previous=has_previous,
    )


1
