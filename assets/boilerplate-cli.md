# CLI Tool Boilerplate

```python
# mycli/__init__.py
"""CLI tool description."""
from __future__ import annotations
__version__ = "0.1.0"

# mycli/__main__.py
from .cli import main
import sys
sys.exit(main())

# mycli/cli.py
from __future__ import annotations
import argparse
from mycli import __version__

def cmd_hello(args: argparse.Namespace) -> int:
    print(f"Hello, {args.name}!")
    return 0

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mycli")
    parser.add_argument("--version", action="version",
                       version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    p_hello = sub.add_parser("hello")
    p_hello.add_argument("name")
    p_hello.set_defaults(func=cmd_hello)
    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
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
