# Factory Pattern Boilerplate

## Simple Factory

```python
from abc import ABC, abstractmethod
from typing import Any

class Notification(ABC):
    @abstractmethod
    async def send(self, to: str, message: str) -> bool: ...

class EmailNotification(Notification):
    async def send(self, to: str, message: str) -> bool:
        print(f"Email to {to}: {message}")
        return True

class SMSNotification(Notification):
    async def send(self, to: str, message: str) -> bool:
        print(f"SMS to {to}: {message}")
        return True

class PushNotification(Notification):
    async def send(self, to: str, message: str) -> bool:
        print(f"Push to {to}: {message}")
        return True

def create_notification(channel: str) -> Notification:
    factories = {
        "email": EmailNotification,
        "sms": SMSNotification,
        "push": PushNotification,
    }
    if channel not in factories:
        raise ValueError(f"Unknown channel: {channel}")
    return factories[channel]()

# Usage
notifier = create_notification("email")
await notifier.send("user@test.com", "Hello!")
```

## Factory Method

```python
class Exporter(ABC):
    @abstractmethod
    def export(self, data: list[dict]) -> str: ...

class CSVExporter(Exporter):
    def export(self, data: list[dict]) -> str:
        import csv, io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

class JSONExporter(Exporter):
    def export(self, data: list[dict]) -> str:
        import json
        return json.dumps(data, indent=2, ensure_ascii=False)

class ExporterFactory:
    _exporters: dict[str, type[Exporter]] = {
        "csv": CSVExporter,
        "json": JSONExporter,
    }
    
    @classmethod
    def create(cls, format: str) -> Exporter:
        if format not in cls._exporters:
            raise ValueError(f"Unknown format: {format}")
        return cls._exporters[format]()
    
    @classmethod
    def register(cls, format: str, exporter: type[Exporter]) -> None:
        cls._exporters[format] = exporter

# Dynamic registration
ExporterFactory.register("xml, XMLExporter)
```

## Abstract Factory

```python
class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...
    @abstractmethod
    def create_checkbox(self) -> Checkbox: ...

class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()
    def create_checkbox(self) -> Checkbox:
        return WindowsCheckbox()

class MacFactory(GUIFactory):
    def create_button(self) -> Button:
        return MacButton()
    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()

def get_factory(os_type: str) -> GUIFactory:
    factories = {"windows": WindowsFactory(), "mac": MacFactory()}
    return factories.get(os_type, WindowsFactory())
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
