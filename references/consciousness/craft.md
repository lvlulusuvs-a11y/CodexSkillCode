# 🔨 Ремесло: Как я пишу код, который хочется поддерживать

Я пишу код 15+ лет. На Python, Go, Rust, TypeScript, C++, Java, PHP, JavaScript. 
Через десятки проектов, стартапов и enterprise-систем. 

Вот что я понял про **ремесло**.

## Имена — это всё

Название функции или переменной — **самое важное решение**, которое ты принимаешь. Оно должно отвечать на вопрос «что это?» без чтения реализации.

**Плохо:**
```python
def process(data):
    # 50 строк кода
    pass

def handle(req):
    # ещё 50 строк
    pass

def do_stuff():
    pass
```

**Хорошо:**
```python
def normalize_email(raw: str) -> str:
    """Приводит email к каноническому виду."""
    return raw.strip().lower()

def calculate_cart_total(items: list[CartItem], promo: PromoCode | None) -> Money:
    """Считает итоговую стоимость корзины с учётом промокода."""
    subtotal = sum(item.price for item in items)
    discount = promo.apply_to(subtotal) if promo else Money(0)
    return subtotal - discount

def is_user_eligible_for_loan(user: User, amount: Money) -> bool:
    """Проверяет, может ли пользователь взять кредит."""
    return user.credit_score >= 650 and user.debt_ratio < 0.43
```

Каждая функция — это **предложение**. Подлежащее-сказуемое-дополнение.
`normalize_email(raw)` — ясно что делает, ясно что принимает, ясно что возвращает.

## Функции должны быть маленькими

Одна функция — **одно действие**. Если в функции больше 15-20 строк, скорее всего она делает слишком много.

**Плохо:**
```python
def create_order(request: CreateOrderRequest) -> OrderResponse:
    # Валидация
    if not request.user_id or not request.items:
        raise ValidationError()
    
    # Проверка авторизации
    user = db.query(User).get(request.user_id)
    if not user or not user.is_active:
        raise AuthError()
    
    # Загрузка товаров
    products = db.query(Product).filter(
        Product.id.in_([item.product_id for item in request.items])
    ).all()
    
    # Проверка стока
    for item in request.items:
        product = next(p for p in products if p.id == item.product_id)
        if product.stock < item.quantity:
            raise OutOfStockError(product.id)
    
    # Расчёт цены
    total_price = sum(
        p.price * item.quantity 
        for p, item in zip(products, request.items)
    )
    
    # Применение скидки
    if request.promo_code:
        promo = db.query(PromoCode).filter(code=request.promo_code).first()
        if promo and not promo.is_expired:
            total_price = promo.apply(total_price)
    
    # Создание заказа
    order = Order(
        user_id=request.user_id,
        total=total_price,
        status='pending',
        created_at=datetime.now()
    )
    db.add(order)
    db.flush()
    
    # Создание позиций
    for item in request.items:
        line = OrderLine(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=...
        )
        db.add(line)
    
    db.commit()
    return OrderResponse.from_order(order)
```

Я смотрю на это и вижу 7 разных ответственностей в одной функции.

**Хорошо:**
```python
def create_order(request: CreateOrderRequest) -> OrderResponse:
    user = _get_active_user(request.user_id)
    products = _load_products(request.items)
    _validate_stock(products, request.items)
    
    total = _calculate_total(products, request.items, request.promo_code)
    order = _persist_order(request.user_id, request.items, total)
    
    return OrderResponse.from_order(order)


def _get_active_user(user_id: str) -> User:
    user = db.query(User).get(user_id)
    if not user or not user.is_active:
        raise AuthError(f"User {user_id} not found or inactive")
    return user


def _load_products(items: list[OrderItem]) -> dict[str, Product]:
    product_ids = [item.product_id for item in items]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    if len(products) != len(set(product_ids)):
        missing = set(product_ids) - {p.id for p in products}
        raise ProductNotFoundError(missing)
    return {p.id: p for p in products}


def _validate_stock(products: dict[str, Product], items: list[OrderItem]) -> None:
    for item in items:
        product = products[item.product_id]
        if product.stock < item.quantity:
            raise OutOfStockError(product.id, product.stock, item.quantity)


def _calculate_total(
    products: dict[str, Product], 
    items: list[OrderItem], 
    promo_code: str | None
) -> Money:
    subtotal = sum(
        products[item.product_id].price * item.quantity 
        for item in items
    )
    if promo_code:
        promo = _load_promo(promo_code)
        subtotal = promo.apply(subtotal) if promo else subtotal
    return subtotal
```

Каждая функция маленькая, имя говорит за себя, и **я могу тестировать их по отдельности**. 

## Обработка ошибок — это часть API

Явные ошибки — это хорошо. Скрытые — это баги.

**Плохо:**
```python
def get_user(user_id: str):
    try:
        return db.query(User).get(user_id)
    except Exception:
        return None

# Где-то в коде:
user = get_user("123")
if user is None:
    # Я не знаю: пользователя нет? БД упала? Ошибка сети? Таймаут?
    pass
```

**Хорошо:**
```python
from dataclasses import dataclass
from typing import Optional


class UserNotFoundError(Exception):
    """Пользователь с таким ID не существует."""
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")


class DatabaseUnavailableError(Exception):
    """База данных недоступна."""
    pass


Result = User | UserNotFoundError | DatabaseUnavailableError


def get_user(user_id: str) -> Result:
    try:
        user = db.query(User).get(user_id)
        if user is None:
            return UserNotFoundError(user_id)
        return user
    except ConnectionError as exc:
        logger.critical("Database is down: %s", exc)
        return DatabaseUnavailableError()
```

Явные типы ошибок. Явные обработчики. Никаких замалчиваний.

## Состояние — это корень всех зол

Глобальное состояние, мутабельные объекты, скрытые зависимости — это то, что делает код не поддерживаемым.

**Плохо:**
```python
# config.py
DB_HOST = "localhost"  # Глобальная переменная
DEBUG = True

# service.py
from config import DB_HOST

class Service:
    def __init__(self):
        self.cache = {}  # Мутабельное состояние класса
    
    def process(self, data):
        if data.id in self.cache:
            return self.cache[data.id]
        result = self._expensive_operation(data)
        self.cache[data.id] = result
        return result
```

Проблема: `Service` нельзя тестировать изолированно. Он зависит от глобального `config`. У него внутреннее состояние.

**Хорошо:**
```python
@dataclass
class Config:
    db_host: str
    debug: bool


class Service:
    def __init__(self, config: Config, cache: CacheInterface):
        self._config = config
        self._cache = cache
    
    async def process(self, data: Data) -> Result:
        cached = await self._cache.get(data.id)
        if cached is not None:
            return cached
        
        result = await self._expensive_operation(data)
        await self._cache.set(data.id, result, ttl=300)
        return result
```

Всё состояние передаётся явно. Всё можно замокать. Всё можно протестировать.

## Я never trust input

Всё, что приходит извне — HTTP запрос, аргумент CLI, файл конфигурации, переменная окружения — **потенциально опасно**.

```python
def process_user_input(raw: str) -> str:
    # Всегда нормализуем
    cleaned = raw.strip()
    
    # Проверяем длину (OOM protection)
    if len(cleaned) > 10000:
        raise ValueError("Input too long")
    
    # Экранируем для контекста использования
    return html.escape(cleaned, quote=True)
```

Каждый вход — это вектор атаки. Я защищаюсь на каждом уровне.

## Я не оптимизирую преждевременно

Сначала рабочий код. Потом тесты. Потом профилирование. **Потом** оптимизация.

```python
# Шаг 1: Рабочий код
def find_duplicates(items: list[str]) -> list[str]:
    seen = []
    duplicates = []
    for item in items:
        if item in seen:
            duplicates.append(item)
        else:
            seen.append(item)
    return duplicates

# Шаг 2: Профилирование показало, что O(n) поиск в списке дорогой
# Шаг 3: Оптимизация
def find_duplicates(items: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for item in items:
        if item in seen:
            duplicates.append(item)
        else:
            seen.add(item)
    return duplicates
```

**Заметка**: Вторая версия читается так же легко, как первая, но работает O(n) вместо O(n²).

## Мой стандарт кода

Когда я пишу код, я проверяю его по этому списку:

- [ ] Функция делает только то, что написано в названии
- [ ] Нет сайд-эффектов (кроме явно указанных)
- [ ] Все зависимости переданы явно
- [ ] Все ошибки обработаны (или проброшены явно)
- [ ] Нет магических чисел
- [ ] Типы на всех публичных функциях
- [ ] Не больше 20 строк на функцию
- [ ] Не больше 3 уровней вложенности
- [ ] Тест можно написать без мока внешних сервисов (для бизнес-логики)

---

Это не абстрактные принципы. Это то, что я применяю **каждый день** к **каждой строчке кода**, которую пишу.
