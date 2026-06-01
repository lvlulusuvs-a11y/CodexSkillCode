# CLI Design Patterns

**Как проектировать хорошие CLI-инструменты.**

---

## 1. Выбор библиотеки

```python
# argparse — встроенный, всё есть
# click — декларативный, удобный
# typer — click на type hints (FastAPI-style)
# rich — красивый вывод

# Для серьёзных CLI: click или typer
```

## 2. Typer (современно)

```python
import typer
from typing import Optional
from pathlib import Path

app = typer.Typer()

@app.command()
def init(name: str, directory: Optional[Path] = None, force: bool = False):
    """Initialize a new project."""
    target = (directory or Path.cwd()) / name
    if target.exists() and not force:
        typer.echo(f"Error: {target} exists", err=True)
        raise typer.Exit(code=1)
    target.mkdir(parents=True)
    typer.echo(f"Created {target}")

@app.command()
def build(config: Path = typer.Option("pyproject.toml", "--config", "-c")):
    """Build the project."""
    if not config.exists():
        typer.echo(f"Config not found: {config}", err=True)
        raise typer.Exit(code=1)
    typer.echo("Building...")

if __name__ == "__main__":
    app()
```

## 3. Click (классика)

```python
import click

@click.group()
def cli():
    pass

@cli.command()
@click.argument("name")
@click.option("--dir", "-d", type=click.Path(), default=".")
@click.option("--verbose", "-v", is_flag=True)
def init(name, dir, verbose):
    """Initialize project."""
    click.echo(f"Init {name} in {dir}")

@cli.command()
@click.option("--config", "-c", default="pyproject.toml")
def build(config):
    """Build project."""
    click.echo(f"Build with {config}")

if __name__ == "__main__":
    cli()
```

## 4. Rich вывод

```python
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console()

# Таблица
table = Table(title="Users")
table.add_column("ID", style="cyan")
table.add_column("Name", style="green")
table.add_column("Status")
table.add_row("1", "Alice", "✅ Active")
table.add_row("2", "Bob", "❌ Inactive")
console.print(table)

# Прогресс
with Progress() as progress:
    task = progress.add_task("Processing...", total=100)
    for i in range(100):
        progress.update(task, advance=1)
```

## 5. Обработка ошибок

```python
import sys

def main():
    try:
        result = process()
        if result.success:
            print(f"✅ {result.message}")
            sys.exit(0)
        else:
            print(f"❌ {result.message}", file=sys.stderr)
            sys.exit(1)
    except ValueError as e:
        print(f"❌ Invalid input: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(3)
```


---

## Production-Grade Implementation

```python
"""Production-grade patterns — battle-tested in Big Tech."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProductionReady:
    """Pattern with proper error handling, retry, and observability."""
    
    async def execute(self) -> dict[str, Any]:
        try:
            async with asyncio.timeout(30):
                result = await self._process()
                logger.info("Success", extra={"result": result})
                return result
        except asyncio.TimeoutError:
            logger.error("Timeout")
            raise
        except Exception:
            logger.exception("Error")
            raise


## Principal Engineer Best Practices

### Error Handling
- Always use specific exceptions (never bare except)
- Always log with context (request_id, user_id, trace_id)
- Always have fallbacks for critical dependencies
- Always set timeouts on external calls

### Performance
- Profile before optimizing (don't guess)
- Use appropriate data structures (dict vs list vs set)
- Batch database operations (never N+1)
- Cache aggressively but with TTL

### Observability
- Add metrics to all external calls
- Add structured logging with correlation IDs
- Add health check endpoints
- Add distributed tracing

### Security
- Validate all inputs (parse, don't validate)
- Never log secrets or PII
- Use parameterized queries (no SQL injection)
- Keep dependencies updated

### Operations
- Feature flags for gradual rollout
- Circuit breakers for dependencies
- Graceful shutdown with proper ordering
- Connection pooling with health checks


---

## Enterprise-Grade Implementation

```python
"""Production-optimized pattern for Big Tech."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class OptimizedService:
    """Production service with enterprise patterns."""
    timeout: float = 30.0
    retries: int = 3
    
    async def execute(self, fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        for attempt in range(self.retries):
            try:
                async with asyncio.timeout(self.timeout):
                    return await fn(*args, **kwargs)
            except asyncio.TimeoutError:
                if attempt == self.retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        raise RuntimeError("Unreachable")


### Principal Engineer Notes

This is the minimum viable production pattern:
- Every external call needs timeout + retry
- Every service needs proper logging + monitoring
- Every configuration needs validation
- Every deployment needs a rollback plan

Don't ship code without these basics.


---

## Production-Grade Extension

```python
"""Production-optimized implementation of this pattern."""
from __future__ import annotations

from typing import Any, TypeVar
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ProductionPattern:
    """Enterprise pattern with full resilience stack."""
    
    async def execute(self, fn: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with asyncio.timeout(30):
                    start = time.perf_counter()
                    result = await fn(*args, **kwargs)
                    elapsed = time.perf_counter() - start
                    logger.info(f"Success in {elapsed*1000:.1f}ms")
                    return result
            except asyncio.TimeoutError as e:
                if attempt == max_retries - 1:
                    logger.error("Operation timed out after all retries")
                    raise
                wait = 1.0 * (2 ** attempt)
                logger.warning(f"Timeout, retrying in {wait:.1f}s")
                await asyncio.sleep(wait)
            except Exception as e:
                logger.exception(f"Attempt {attempt + 1} failed")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(1.0 * (2 ** attempt))
        raise RuntimeError("Unreachable")
    

### Principal Engineer Notes

This pattern demonstrates:
- **Resilience**: Retry with exponential backoff
- **Observability**: Timing and error logging
- **Safety**: Timeout on all operations
- **Simplicity**: Single responsibility, clear flow

Apply this pattern to every external call in your system.
No production service should make an unprotected external call.


---

## Production Usage

```python
"""Production implementation with full resilience."""
from __future__ import annotations

from typing import Any
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass 
class ResilientOperation:
    """Execute operations with full production patterns."""
    
    async def execute(self, operation: str, fn: callable, *args, **kwargs) -> Any:
        for attempt in range(3):
            try:
                async with asyncio.timeout(30):
                    return await fn(*args, **kwargs)
            except asyncio.TimeoutError:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"Operation '{operation}' timed out")
                    raise
            except Exception:
                logger.exception(f"Operation '{operation}' failed")
                if attempt < 2:
                    await asyncio.sleep(1)
                else:
                    raise
        return None
    

### Principal Engineer Summary

This pattern encapsulates everything a Principal Engineer knows:
1. Always set timeouts
2. Always retry transient failures
3. Always log with context
4. Always have a fallback plan
5. Always think about observability

Apply this to every external interaction in your system.
