from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar


@dataclass
class ResourceQueryOptions:
    """Query options for listing memories, glossaries and styleguides with optional name filtering and pagination.

    :param search: Filter resources by their displayed name using a case- and accent-insensitive
        substring match. Spaces are preserved. Enables pagination when provided.
    :param page: Page number (1-based). Enables pagination when provided.
    :param size: Page size (1-200). Enables pagination when provided.
    """

    search: Optional[str] = None
    page: Optional[int] = None
    size: Optional[int] = None


_T = TypeVar('_T')


@dataclass
class CollectionResult(Generic[_T]):
    """Collection of resources with optional pagination metadata.

    :param total: Total number of matching resources.
    :param page: Current page (1-based), or None for an unpaginated response.
    :param size: Page size, or None for an unpaginated response.
    """

    items: List[_T]
    total: int
    page: Optional[int] = None
    size: Optional[int] = None
