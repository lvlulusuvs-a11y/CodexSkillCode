# Library Package Boilerplate

```
mypackage/
├── __init__.py        # публичное API
├── _internal/
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
├── types.py           # кастомные типы
├── exceptions.py      # свои исключения
└── tests/
```

```python
# mypackage/__init__.py
from __future__ import annotations
from mypackage._internal.core import MyClass
from mypackage._internal.utils import helper_func
from mypackage.types import Config
from mypackage.exceptions import MyPackageError

__version__ = "0.1.0"
__all__ = ["MyClass", "helper_func", "Config", "MyPackageError"]

# mypackage/_internal/core.py
from __future__ import annotations
from mypackage.types import Config
from mypackage.exceptions import MyPackageError

class MyClass:
    def __init__(self, config: Config) -> None:
        self._config = config

    def run(self) -> str:
        if not self._config.valid:
            raise MyPackageError("Invalid config")
        return "ok"

# mypackage/types.py
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Config:
    host: str = "localhost"
    port: int = 8080

    @property
    def valid(self) -> bool:
        return self.port > 0

# mypackage/exceptions.py
from __future__ import annotations

class MyPackageError(Exception):
    """Base exception for mypackage."""
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
