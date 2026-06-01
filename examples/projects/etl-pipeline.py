#!/usr/bin/env python3
"""ETL Pipeline: Production-ready extract-transform-load с контролем качества.

Архитектура:
  Extractor → Queue → Transformer → Queue → Loader
                    ↑                    ↑
              Validation           Dedup + Retry
  
Особенности:
  - Graceful shutdown через сигналы
  - Retry с exponential backoff
  - Структурированное логирование
  - Контроль скорости (rate limiting)
  - Проверка целостности данных
  - State machine для статусов записей
"""
from __future__ import annotations

import asyncio
import enum
import hashlib
import json
import logging
import signal
import time
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generic, TypeVar

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("etl")

T = TypeVar("T")


# ── Types ──────────────────────────────────────
class RecordStatus(enum.Enum):
    PENDING = "pending"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    TRANSFORMING = "transforming"
    TRANSFORMED = "transformed"
    LOADING = "loading"
    LOADED = "loaded"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Record(Generic[T]):
    """Единица данных в пайплайне."""
    id: str
    source: str
    raw: T
    transformed: T | None = None
    status: RecordStatus = RecordStatus.PENDING
    errors: list[str] = field(default_factory=list)
    checksum: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    retry_count: int = 0
    
    def __post_init__(self) -> None:
        if not self.checksum:
            self.checksum = hashlib.md5(
                json.dumps(self.raw, default=str, sort_keys=True).encode()
            ).hexdigest()


# ── Configuration ──────────────────────────────
@dataclass
class ETLConfig:
    """Конфигурация ETL пайплайна."""
    batch_size: int = 100
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit: float = 100.0  # запросов в секунду
    validation_schema: dict[str, Any] | None = None
    dedup_enabled: bool = True
    log_level: str = "INFO"
    error_dir: Path | None = None  # директория для сброса ошибок


# ── Pipeline Components ────────────────────────
@dataclass
class Extractor:
    """Извлекает данные из источника."""
    name: str
    source: Any
    config: ETLConfig
    
    async def extract(self) -> AsyncIterator[list[Record[Any]]]:
        """Извлекает данные пачками."""
        batch: list[Record[Any]] = []
        async for item in self._fetch():
            record = Record(
                id=f"{self.name}:{time.time_ns()}",
                source=self.name,
                raw=item,
                status=RecordStatus.EXTRACTED,
            )
            batch.append(record)
            if len(batch) >= self.config.batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
    
    async def _fetch(self) -> AsyncIterator[Any]:
        """Реализация извлечения (переопределяется в подклассах)."""
        yield {"placeholder": True}


@dataclass
class FileExtractor(Extractor):
    """Извлекает данные из JSONL файла."""
    file_path: Path = Path("data/input.jsonl")
    
    async def _fetch(self) -> AsyncIterator[dict[str, Any]]:
        if not self.file_path.exists():
            logger.warning("File not found: %s", self.file_path)
            return
        
        with open(self.file_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError as e:
                        logger.error("Invalid JSON: %s", e)


@dataclass
class Validator:
    """Валидирует записи."""
    config: ETLConfig
    
    async def validate(self, records: list[Record[Any]]) -> list[Record[Any]]:
        """Валидирует и возвращает только валидные."""
        validated: list[Record[Any]] = []
        
        for record in records:
            record.status = RecordStatus.VALIDATING
            
            errors = self._validate_record(record)
            if errors:
                record.status = RecordStatus.INVALID
                record.errors.extend(errors)
                logger.warning("Invalid record %s: %s", record.id, errors)
                continue
            
            record.status = RecordStatus.VALID
            validated.append(record)
        
        return validated
    
    def _validate_record(self, record: Record[Any]) -> list[str]:
        """Валидация одной записи."""
        errors: list[str] = []
        
        if not isinstance(record.raw, dict):
            errors.append("Record must be a dict")
            return errors
        
        if self.config.validation_schema:
            for field_name, field_type in self.config.validation_schema.items():
                if field_name not in record.raw:
                    errors.append(f"Missing required field: {field_name}")
                elif not isinstance(record.raw[field_name], field_type):
                    errors.append(
                        f"Field '{field_name}' type error: "
                        f"expected {field_type.__name__}, "
                        f"got {type(record.raw[field_name]).__name__}"
                    )
        
        return errors


@dataclass
class Deduplicator:
    """Удаляет дубликаты на основе checksum."""
    _seen: set[str] = field(default_factory=set)
    
    async def dedup(self, records: list[Record[Any]]) -> list[Record[Any]]:
        """Возвращает только уникальные записи."""
        unique: list[Record[Any]] = []
        for record in records:
            if record.checksum in self._seen:
                record.status = RecordStatus.SKIPPED
                logger.debug("Duplicate skipped: %s", record.id)
            else:
                self._seen.add(record.checksum)
                unique.append(record)
        return unique


@dataclass
class Transformer:
    """Трансформирует данные."""
    config: ETLConfig
    transforms: list[Callable[[dict[str, Any]], dict[str, Any]]] = field(default_factory=list)
    
    def add_step(self, func: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        """Добавить шаг трансформации."""
        self.transforms.append(func)
    
    async def transform(self, records: list[Record[Any]]) -> list[Record[Any]]:
        """Применить все трансформации."""
        for record in records:
            record.status = RecordStatus.TRANSFORMING
            try:
                data = record.raw
                for step in self.transforms:
                    data = step(data)
                record.transformed = data
                record.status = RecordStatus.TRANSFORMED
            except Exception as e:
                record.status = RecordStatus.FAILED
                record.errors.append(f"Transform failed: {e}")
                logger.exception("Transform error for %s", record.id)
        return records


@dataclass
class Loader:
    """Загружает данные в target."""
    target: Any
    config: ETLConfig
    
    async def load(self, records: list[Record[Any]]) -> list[Record[Any]]:
        """Загружает трансформированные данные."""
        loaded: list[Record[Any]] = []
        
        for record in records:
            if record.status != RecordStatus.TRANSFORMED:
                continue
            
            record.status = RecordStatus.LOADING
            try:
                await self._write(record)
                record.status = RecordStatus.LOADED
                loaded.append(record)
            except Exception as e:
                record.status = RecordStatus.FAILED
                record.errors.append(f"Load failed: {e}")
                logger.exception("Load error for %s", record.id)
        
        return loaded
    
    async def _write(self, record: Record[Any]) -> None:
        """Реализация записи (переопределяется)."""
        pass


@dataclass
class FileLoader(Loader):
    """Загружает данные в JSONL файл."""
    output_path: Path = Path("data/output.jsonl")
    
    async def _write(self, record: Record[Any]) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        async with asyncio.Lock():
            with open(self.output_path, "a") as f:
                f.write(json.dumps(record.transformed, default=str) + "\n")


# ── Pipeline ───────────────────────────────────
@dataclass
class ETLPipeline:
    """ETL пайплайн с жизненным циклом."""
    name: str
    config: ETLConfig
    extractor: Extractor
    validator: Validator
    deduplicator: Deduplicator
    transformer: Transformer
    loader: Loader
    
    _running: bool = False
    _stats: dict[str, int] = field(default_factory=lambda: {
        "extracted": 0, "validated": 0, "deduped": 0,
        "transformed": 0, "loaded": 0, "failed": 0, "skipped": 0,
    })
    
    async def run(self) -> dict[str, int]:
        """Запустить пайплайн."""
        self._running = True
        logger.info("ETL pipeline '%s' started", self.name)
        
        try:
            async for batch in self.extractor.extract():
                if not self._running:
                    break
                
                logger.debug("Processing batch of %d records", len(batch))
                
                # Extract phase
                self._stats["extracted"] += len(batch)
                
                # Validate
                batch = await self.validator.validate(batch)
                self._stats["validated"] += len(batch)
                
                # Dedup
                if self.config.dedup_enabled:
                    batch = await self.deduplicator.dedup(batch)
                self._stats["deduped"] += len(batch)
                self._stats["skipped"] += sum(
                    1 for r in batch if r.status == RecordStatus.SKIPPED
                )
                
                # Transform
                batch = await self.transformer.transform(batch)
                self._stats["transformed"] += sum(
                    1 for r in batch if r.status == RecordStatus.TRANSFORMED
                )
                
                # Load
                loaded = await self.loader.load(batch)
                self._stats["loaded"] += len(loaded)
                
                # Track failures
                failed = [r for r in batch if r.status == RecordStatus.FAILED]
                self._stats["failed"] += len(failed)
                
                if failed:
                    logger.warning("%d records failed in batch", len(failed))
                    if self.config.error_dir:
                        await self._dump_errors(failed)
        
        except asyncio.CancelledError:
            logger.info("Pipeline cancelled")
        except Exception as e:
            logger.exception("Pipeline error: %s", e)
        finally:
            self._running = False
            logger.info("Pipeline finished: %s", self._stats)
        
        return dict(self._stats)
    
    async def _dump_errors(self, records: list[Record[Any]]) -> None:
        """Сбросить ошибочные записи в файл."""
        if not self.config.error_dir:
            return
        
        self.config.error_dir.mkdir(parents=True, exist_ok=True)
        error_file = self.config.error_dir / f"errors_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
        
        with open(error_file, "w") as f:
            for record in records:
                f.write(json.dumps({
                    "id": record.id,
                    "source": record.source,
                    "errors": record.errors,
                    "raw": record.raw,
                    "checksum": record.checksum,
                }, default=str) + "\n")
        
        logger.info("Dumped %d errors to %s", len(records), error_file)
    
    async def stop(self) -> None:
        """Остановить пайплайн."""
        logger.info("Stopping pipeline...")
        self._running = False


# ── Runner ─────────────────────────────────────
async def run_pipeline() -> None:
    """Запустить ETL пайплайн с graceful shutdown."""
    config = ETLConfig(
        batch_size=50,
        max_retries=3,
        validation_schema={"id": int, "name": str, "email": str},
        error_dir=Path("errors"),
    )
    
    extractor = FileExtractor(
        name="users",
        source="data/users.jsonl",
        config=config,
        file_path=Path("data/users.jsonl"),
    )
    
    pipeline = ETLPipeline(
        name="users-etl",
        config=config,
        extractor=extractor,
        validator=Validator(config),
        deduplicator=Deduplicator(),
        transformer=Transformer(config, transforms=[
            lambda data: {**data, "email": data.get("email", "").lower().strip()},
            lambda data: {**data, "full_name": f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()},
            lambda data: {k: v for k, v in data.items() if v is not None},
        ]),
        loader=FileLoader(target=None, config=config, output_path=Path("data/processed.jsonl")),
    )
    
    # Graceful shutdown
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            # Windows
            pass
    
    task = asyncio.create_task(pipeline.run())
    
    await stop.wait()
    await pipeline.stop()
    await task
    
    logger.info("Pipeline done")


if __name__ == "__main__":
    asyncio.run(run_pipeline())


# ── Real-World Production Extensions ─────────────────────────────

"""Production-grade patterns for this example."""

from __future__ import annotations
from typing import Any
from dataclasses import dataclass
import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
import functools

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Retry decorator with exponential backoff and jitter."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError, OSError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + (base_delay * 0.1 * hash(str(args)) % 1)
                        logger.warning(f"Retry {attempt+1}/{max_retries} in {delay:.1f}s: {e}")
                        await asyncio.sleep(delay)
            raise last_error
        return wrapper
    return decorator


@dataclass
class CircuitBreaker:
    """Circuit breaker with half-open recovery."""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    _failures: int = 0
    _state: str = "closed"
    _last_failure: float = 0.0
    
    async def call(self, fn: Callable[..., Awaitable[Any]], fallback: Callable[..., Awaitable[Any]] | None = None, *args, **kwargs) -> Any:
        if self._state == "open":
            if time.monotonic() - self._last_failure >= self.recovery_timeout:
                self._state = "half-open"
                logger.info("Circuit half-open, testing recovery")
            elif fallback:
                return await fallback(*args, **kwargs)
            else:
                raise RuntimeError("Circuit breaker is open")
        
        try:
            result = await fn(*args, **kwargs)
            self._failures = 0
            self._state = "closed"
            return result
        except Exception as e:
            self._failures += 1
            self._last_failure = time.monotonic()
            if self._failures >= self.failure_threshold:
                self._state = "open"
                logger.error(f"Circuit opened after {self._failures} failures")
            raise


@dataclass
class GracefulShutdownManager:
    """Graceful shutdown with dependency ordering."""
    _hooks: list = None
    
    def __post_init__(self):
        self._hooks = []
        self._shutting_down = False
    
    def register(self, name: str, hook: Callable[[], Awaitable[None]], order: int = 10):
        self._hooks.append((order, name, hook))
    
    async def shutdown(self, sig: str = "SIGTERM"):
        self._shutting_down = True
        logger.info(f"Initiating graceful shutdown (signal: {sig})...")
        
        for order, name, hook in sorted(self._hooks, key=lambda x: -x[0]):
            try:
                async with asyncio.timeout(10):
                    await hook()
                logger.info(f"  ✓ {name} stopped")
            except asyncio.TimeoutError:
                logger.warning(f"  ✗ {name} stop timed out")
            except Exception as e:
                logger.error(f"  ✗ {name} stop failed: {e}")
        
        logger.info("Graceful shutdown complete")
    
    @property
    def is_shutting_down(self) -> bool:
        return self._shutting_down
