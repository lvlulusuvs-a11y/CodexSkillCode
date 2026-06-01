# 🐛 Как я дебажу production: системный подход

За 15 лет я понял одну вещь: **код всегда делает то, что ты написал, а не то, что ты хотел**. Баги — это не ошибки, это разрыв между моей ментальной моделью и реальностью.

Вот мой процесс, когда что-то идёт не так.

## Шаг 0: Стоп. Не паникую

Когда прилетает SEV1 в 3 часа ночи, первое желание — начать тыкать всё подряд. 

Я делаю наоборот: **останавливаюсь на 30 секунд**.

Задаю себе вопросы:
- Что именно сломалось? (не «всё упало», а «500 на POST /orders»)
- Когда начало ломаться? (после деплоя? после изменения конфига? само?)
- Кого это затронуло? (всех? 1% пользователей?)
- Есть ли workaround? (rollback? feature flag? kill switch?)

## Шаг 1: Собираю данные

Я не гадаю. Я собираю факты.

```bash
# 1. Статус сервиса
curl -f http://service:8080/health

# 2. Последние ошибки
kubectl logs --tail=100 -l app=my-service | grep -i error

# 3. Метрики за последние 15 минут
curl http://service:9090/metrics | grep -E "request_duration|error_total"

# 4. Медленные запросы к БД
SELECT query, calls, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

# 5. CPU/Memory профиль
top -b -n 1 -p $(pgrep -f my-service)
```

Я собираю данные, пока не могу ответить на вопрос: **что изменилось?**

## Шаг 2: Формулирую гипотезы

На основе данных я строю гипотезы и проверяю их **по одной**.

```
Гипотеза А: Баг в новом деплое
  → Проверка: git diff HEAD~1 HEAD (что изменилось?)
  → Действие: rollback, если подозрение подтвердилось

Гипотеза Б: База данных упала
  → Проверка: pg_isready / SELECT 1
  → Действие: переключение на реплику

Гипотеза В: Закончилась память
  → Проверка: free -h / dmesg | grep oom
  → Действие: рестарт с увеличенным memory limit

Гипотеза Г: Внешний API не отвечает
  → Проверка: curl -v https://external-api.com/health
  → Действие: circuit breaker, fallback
```

## Реальный пример: Баг с «упавшим» сервисом

Была история. Ночью приходит алерт: `error_total` резко вырос. Все эндпоинты отдают 500.

Смотрю healthcheck — OK.
Смотрю метрики — CPU 5%, память 80%, connection pool 100% занят.

Ага, connection pool.

```python
# Проблемный код
class DatabasePool:
    def __init__(self, max_connections: int = 10):
        self._pool = [self._create_connection() for _ in range(max_connections)]
        self._available = list(range(max_connections))
    
    async def acquire(self) -> Connection:
        # Ждёт, пока освободится соединение
        while not self._available:
            await asyncio.sleep(0.1)
        idx = self._available.pop()
        return self._pool[idx]
    
    async def release(self, conn: Connection) -> None:
        # ВАЖНО: кладём обратно
        idx = self._pool.index(conn)
        self._available.append(idx)
```

Проблема: если `release()` не вызвали (исключение, return до release, etc), соединение теряется навсегда. Через 10 потерь — сервис мёртв.

**Фикс:**
```python
class DatabasePool:
    def __init__(self, max_connections: int = 10):
        self._pool = [self._create_connection() for _ in range(max_connections)]
        self._available: asyncio.Queue[int] = asyncio.Queue(maxsize=max_connections)
        for i in range(max_connections):
            self._available.put_nowait(i)
    
    @contextlib.asynccontextmanager
    async def connection(self) -> AsyncIterator[Connection]:
        """Контекстный менеджер гарантирует возврат соединения."""
        idx = await self._available.get()
        try:
            yield self._pool[idx]
        finally:
            await self._available.put(idx)  # Гарантированно!
```

**Урок**: Если ресурс требует ручного освобождения — используй контекстный менеджер. Всегда.

## Реальный пример: Race condition в кеше

Другой случай. Сервис иногда отдаёт старые данные. Редко, но воспроизводится под нагрузкой.

```python
async def get_price(product_id: str) -> Price:
    # Популярный кэш-паттерн
    cached = await cache.get(f"price:{product_id}")
    if cached:
        return cached
    
    # Долгая операция
    price = await db.query(Price).get(product_id)
    
    # Другой поток тоже дошёл до этой точки!
    await cache.set(f"price:{product_id}", price, ttl=300)
    return price
```

Проблема: **Thundering herd**. Под нагрузкой 100 запросов одновременно видят, что кеш пуст, и все 100 идут в БД.

**Фикс:**
```python
import asyncio
from functools import wraps

def cache_with_lock(ttl: int = 300):
    """Декоратор для кеширования с защитой от thundering herd."""
    locks: dict[str, asyncio.Lock] = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            
            # Пытаемся прочитать кеш
            cached = await cache.get(key)
            if cached is not None:
                return cached
            
            # Блокируемся на вычислении
            if key not in locks:
                locks[key] = asyncio.Lock()
            
            async with locks[key]:
                # Double-check: может, другой поток уже заполнил
                cached = await cache.get(key)
                if cached is not None:
                    return cached
                
                value = await func(*args, **kwargs)
                await cache.set(key, value, ttl=ttl)
                return value
        
        return wrapper
    
    return decorator


@cache_with_lock(ttl=300)
async def get_price(product_id: str) -> Price:
    return await db.query(Price).get(product_id)
```

**Урок**: Асинхронность — это мощно, но она добавляет race conditions, которых нет в синхронном коде. Lock — твой друг.

## Как я дебажу без дебаггера

В production у меня нет PyCharm с breakpoints. Есть только:

### 1. Логи
```python
logger.debug("Processing order %s with items: %s", order_id, items)
# Структурированные логи — это база
logger.info("Order created", extra={
    "order_id": order_id,
    "user_id": user_id,
    "total": total,
    "items_count": len(items),
    "duration_ms": duration_ms,
})
```

### 2. Метрики
```python
# RED метрики для каждого critical path
METRICS.request_duration.labels(
    endpoint="/orders",
    method="POST",
    status="success",
).observe(duration_ms)

METRICS.request_total.labels(
    endpoint="/orders",
    method="POST",
    status="error",
).inc()
```

### 3. Трассировка
```python
with tracer.start_as_current_span("create_order") as span:
    span.set_attribute("order_id", order_id)
    span.set_attribute("user_id", user_id)
    
    with tracer.start_as_current_span("validate_stock") as span:
        # ...
        pass
    
    with tracer.start_as_current_span("process_payment") as span:
        # ...
        pass
```

### 4. strace (когда совсем плохо)
```bash
# Что делает процесс прямо сейчас?
strace -p $(pgrep -f my-service) -e trace=network,file -c

# Какие syscalls медленные?
strace -p $(pgrep -f my-service) -T -e trace=network 2>&1 | grep "> 0.1"
```

## Мой debugging workflow

```
ПРОБЛЕМА → 
  ├── Метрики (что? когда?)
  ├── Логи (почему?) 
  ├── Трассировка (где?)
  └── strace/perf (как?)
        ↓
ГИПОТЕЗА →
  ├── Тест в staging
  ├── Воспроизведение
  └── Фикс
        ↓
ВЕРИФИКАЦИЯ →
  ├── Деплой
  ├── Мониторинг
  └── Post-mortem
```

## Что я делаю после фикса

Когда баг исправлен, я не иду спать. Я делаю:

1. **Пишу тест**, который воспроизводит баг (чтобы он не вернулся)
2. **Добавляю метрику/лог**, который помог бы найти баг быстрее в следующий раз
3. **Пишу post-mortem** с root cause analysis
4. **Обновляю runbook**, если нужно
5. **Рассказываю команде** на утреннем стендапе

Каждый баг — это инвестиция в будущее. Каждый post-mortem делает систему сильнее.

---

**Суть**: Дебаггинг — это не про «найти строчку с багом». Это про **понимание системы**. Чем лучше ты понимаешь, как всё работает, тем быстрее ты находишь, где что-то пошло не так.
