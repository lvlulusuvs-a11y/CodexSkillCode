# Функции, которые не стыдно показать маме

Я переписывал тонны чужого кода. Единственное, что неизменно делает код хорошим или плохим - функции. Не классы, не архитектура, не фреймворк. Функции.

## Симптомы плохой функции

Я открываю файл и вижу:

```python
def process_data(data, options=None):
    # 80 строк невнятной логики
    ...
```

У меня уже всё внутри переворачивается. Потому что:
1. `process_data` - самое бесполезное имя в программировании
2. `data` - что за data? Строка? Объект? Список?
3. `options=None` - какие опции? Где документация?
4. 80 строк - значит делает минимум 3 разных дела

## Что я делаю вместо этого

### 1. Имя = глагол + существительное

```python
# Плохо
def process(data): ...
def handle(req): ...
def do_stuff(): ...

# Хорошо
def calculate_cart_total(cart: Cart) -> Money: ...
def send_password_reset(email: Email) -> Result: ...
def validate_promocode(code: str, cart: Cart) -> bool: ...
def parse_webhook_event(raw: dict) -> WebhookEvent: ...
def normalize_email(address: str) -> str: ...
```

Имя функции - это обещание. Ты обещаешь сделать именно то, что написано в имени, и ничего больше.

### 2. Один уровень абстракции

Функция не должна смешивать high-level и low-level детали. Если функция одновременно управляет HTTP запросами и SQL запросами - это проблема.

```python
# Плохо: менеджерский код с SQL внутри
def get_active_users():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, email
        FROM users
        WHERE is_active = true
    """)
    return cur.fetchall()
```

```python
# Хорошо: разделение уровней
def get_active_users() -> list[User]:
    raw = await user_repository.find_active(days=30)
    return [User.from_row(row) for row in raw]
```

### 3. return раньше чем else

```python
# Плохо: лишняя вложенность
def get_discount(user: User) -> Money:
    if user.is_vip:
        if user.years > 5:
            return Money(50)
        else:
            return Money(30)
    else:
        return Money(0)
```

```python
# Хорошо: return as soon as possible
def get_discount(user: User) -> Money:
    if not user.is_vip:
        return Money(0)
    if user.years > 5:
        return Money(50)
    return Money(30)
```

### 4. Параметры: меньше трёх

```python
# Плохо: 6 параметров
def create_user(name, email, password, role, is_active, notify):
    ...

# Хорошо: request object
@dataclass
class CreateUserRequest:
    name: str
    email: EmailAddress
    password: Password
    role: Role

def create_user(request: CreateUserRequest) -> User:
    ...
```

### 5. Чистые функции - это идеал

Чистая функция = один и тот же input всегда даёт один и тот же output + нет сайд-эффектов.

```python
# Грязная: зависит от глобального состояния
def get_price(product_id: str) -> Money:
    discount = CURRENT_PROMO
    return base_price * (1 - discount)
```

```python
# Чистая: все зависимости явные
def get_price(base_price: Money, discount_rate: float) -> Money:
    return base_price * (1 - discount_rate)
```

## Мой лимит: 20 строк

Я никогда не пишу функцию длиннее 20 строк. Если функция выходит за лимит - выношу часть логики в отдельную функцию.

## Вывод

Функция - это как клетка в организме. Она самодостаточна, делает одну вещь, и взаимодействует с другими клетками через чёткий интерфейс. Если твой код - это монстр из 200-строчных функций - ты умрёшь под грузом собственной архитектуры.


## Дополнительный материал

Продолжая тему, стоит отметить что на практике это работает не всегда идеально.
Есть много нюансов, которые зависят от конкретного контекста: нагрузка, команда,
бюджет, существующая архитектура.

### Практический пример

Рассмотрим реальный случай. Допустим у нас есть сервис платежей.
Мы решили применить паттерн из этой статьи. На первый взгляд все работает отлично.
Но под нагрузкой 1000 rps мы видим странное поведение: latency p95 вырос в 3 раза.

#### Метрики до и после

```
Метрика     До     После
p50         12ms   15ms
p95         45ms   140ms
p99         80ms   250ms
Error rate  0.01%  2.3%
```

### Анализ

После profiling и tracing мы выяснили что проблема в connection pool.
Каждый вызов создавал новое соединение, потому что пул был настроен неправильно.
Мы увеличили pool_size с 5 до 20 и latency вернулась в норму.

### Вывод

Любой паттерн работает только если ты понимаешь его внутреннее устройство
и правильно настраиваешь под свою нагрузку. Копировать код без понимания -
путь к катастрофе.

### Дополнительный код

```python
import asyncio
import random
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Config:
    pool_size: int = 10
    max_retries: int = 3
    timeout: float = 5.0
    circuit_breaker_threshold: int = 5


class Service:
    def __init__(self, config: Config):
        self.config = config
        self._pool = []
        self._healthy = True

    async def start(self):
        self._pool = [await self._create_connection()
                      for _ in range(self.config.pool_size)]
        logger.info("Started with pool of %d connections",
                    self.config.pool_size)

    async def _create_connection(self):
        await asyncio.sleep(0.1)
        return {"id": random.randint(1, 10000)}

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        for attempt in range(self.config.max_retries):
            try:
                async with asyncio.timeout(self.config.timeout):
                    return await func(*args, **kwargs)
            except asyncio.TimeoutError:
                logger.warning("Timeout on attempt %d", attempt + 1)
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt + random.uniform(0, 0.5))

    async def healthcheck(self) -> dict:
        return {
            "healthy": self._healthy,
            "pool_size": len(self._pool),
        }
```

### Ключевые метрики

| Метрика | Значение | Когда бить тревогу |
|---------|----------|-------------------|
| p50 latency | <50ms | >100ms |
| p99 latency | <200ms | >500ms |
| Error rate | <0.1% | >1% |
| CPU usage | <70% | >80% |
| Memory usage | <80% | >90% |
| Pool usage | <80% | >90% |

Этот паттерн я использую постоянно. Он работает, но требует глубокого понимания.

### Связанные темы

- Connection pooling strategies
- Circuit breaker pattern
- Retry with exponential backoff
- Bulkhead isolation pattern
- Timeout propagation



## Дополнительный материал

Продолжая тему, стоит отметить что на практике это работает не всегда идеально.
Есть много нюансов, которые зависят от конкретного контекста: нагрузка, команда,
бюджет, существующая архитектура.

### Практический пример

Рассмотрим реальный случай. Допустим у нас есть сервис платежей.
Мы решили применить паттерн из этой статьи. На первый взгляд все работает отлично.
Но под нагрузкой 1000 rps мы видим странное поведение: latency p95 вырос в 3 раза.

#### Метрики до и после

```
Метрика     До     После
p50         12ms   15ms
p95         45ms   140ms
p99         80ms   250ms
Error rate  0.01%  2.3%
```

### Анализ

После profiling и tracing мы выяснили что проблема в connection pool.
Каждый вызов создавал новое соединение, потому что пул был настроен неправильно.
Мы увеличили pool_size с 5 до 20 и latency вернулась в норму.

### Вывод

Любой паттерн работает только если ты понимаешь его внутреннее устройство
и правильно настраиваешь под свою нагрузку. Копировать код без понимания -
путь к катастрофе.

### Дополнительный код

```python
import asyncio
import random
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Config:
    pool_size: int = 10
    max_retries: int = 3
    timeout: float = 5.0
    circuit_breaker_threshold: int = 5


class Service:
    def __init__(self, config: Config):
        self.config = config
        self._pool = []
        self._healthy = True

    async def start(self):
        self._pool = [await self._create_connection()
                      for _ in range(self.config.pool_size)]
        logger.info("Started with pool of %d connections",
                    self.config.pool_size)

    async def _create_connection(self):
        await asyncio.sleep(0.1)
        return {"id": random.randint(1, 10000)}

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        for attempt in range(self.config.max_retries):
            try:
                async with asyncio.timeout(self.config.timeout):
                    return await func(*args, **kwargs)
            except asyncio.TimeoutError:
                logger.warning("Timeout on attempt %d", attempt + 1)
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt + random.uniform(0, 0.5))

    async def healthcheck(self) -> dict:
        return {
            "healthy": self._healthy,
            "pool_size": len(self._pool),
        }
```

### Ключевые метрики

| Метрика | Значение | Когда бить тревогу |
|---------|----------|-------------------|
| p50 latency | <50ms | >100ms |
| p99 latency | <200ms | >500ms |
| Error rate | <0.1% | >1% |
| CPU usage | <70% | >80% |
| Memory usage | <80% | >90% |
| Pool usage | <80% | >90% |

Этот паттерн я использую постоянно. Он работает, но требует глубокого понимания.

### Связанные темы

- Connection pooling strategies
- Circuit breaker pattern
- Retry with exponential backoff
- Bulkhead isolation pattern
- Timeout propagation

