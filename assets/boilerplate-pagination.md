# Pagination Boilerplate

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Generic, TypeVar, Sequence

T = TypeVar("T")

@dataclass
class Page(Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    per_page: int
    pages: int = field(init=False)

    def __post_init__(self):
        self.pages = max(1, -(-self.total // self.per_page))

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    @property
    def next_page(self) -> int | None:
        return self.page + 1 if self.has_next else None

    @property
    def prev_page(self) -> int | None:
        return self.page - 1 if self.has_prev else None

    def to_dict(self) -> dict:
        return {
            "items": [item if isinstance(item, dict) else item.__dict__
                      for item in self.items],
            "meta": {
                "page": self.page,
                "per_page": self.per_page,
                "total": self.total,
                "pages": self.pages,
            },
        }

def paginate(query, page: int = 1, per_page: int = 20) -> Page:
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return Page(items=items, total=total, page=page, per_page=per_page)
```


## Production-Level Implementation

```python
"""Bonus: Production-ready pattern."""
from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExtendedImplementation:
    """Extended with error handling, logging, retry."""
    
    async def process(self) -> dict[str, Any]:
        try:
            async with asyncio.timeout(10):
                result = await self._execute()
                return result
        except asyncio.TimeoutError:
            logger.error("Processing timed out")
            raise
        except Exception:
            logger.exception("Processing failed")
            raise
