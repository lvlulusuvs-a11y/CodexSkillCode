# Clean Architecture: Practical Implementation

Clean Architecture is not about layers and interfaces. It is about dependency
inversion: business logic should not depend on frameworks, databases, or HTTP.

## The Core Idea

```
External (DB, HTTP, Queue) ---> Application (use cases) ---> Domain (entities)
                               Dependencies point INWARD
```

The domain has zero external dependencies. The application layer depends on
abstractions, not implementations. The outer layer wires everything together.

## Domain Layer (Pure Business Logic)

```python
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class OrderLine:
    product_id: str
    quantity: int
    unit_price: Decimal

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Order:
    id: str
    user_id: str
    lines: list[OrderLine]
    status: OrderStatus
    created_at: datetime

    @property
    def total(self) -> Decimal:
        return sum(line.total for line in self.lines)

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise ValueError(f"Cannot confirm order in {self.status}")
        self.status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
            raise ValueError(f"Cannot cancel order in {self.status}")
        self.status = OrderStatus.CANCELLED
```

Domain has zero imports from FastAPI, SQLAlchemy, or anything external.
Pure Python. Easy to test.

## Application Layer (Use Cases)

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod


# Ports (interfaces)
class OrderRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> None: ...

    @abstractmethod
    async def get_by_id(self, order_id: str) -> Order | None: ...


class PaymentGateway(ABC):
    @abstractmethod
    async def charge(self, amount: Decimal, token: str) -> str: ...


# Use case
@dataclass
class CreateOrderUseCase:
    order_repo: OrderRepository
    payment_gw: PaymentGateway

    async def execute(self, user_id: str, items: list[dict]) -> Order:
        # Create order
        order = Order(
            id=str(uuid.uuid4()),
            user_id=user_id,
            lines=[
                OrderLine(
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    unit_price=Decimal(str(item["price"])),
                )
                for item in items
            ],
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        # Save
        await self.order_repo.save(order)

        # Charge
        try:
            payment_id = await self.payment_gw.charge(
                order.total, "token_placeholder"
            )
            order.confirm()
            await self.order_repo.save(order)
        except Exception:
            order.cancel()
            await self.order_repo.save(order)
            raise

        return order
```

The use case depends on abstractions (OrderRepository, PaymentGateway),
not on their implementations (PostgresRepository, StripeGateway).

## Infrastructure Layer

```python
class PostgresOrderRepository(OrderRepository):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def save(self, order: Order) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO orders (id, user_id, status, total, created_at) "
                "VALUES ($1, $2, $3, $4, $5) "
                "ON CONFLICT (id) DO UPDATE SET status = $3",
                order.id, order.user_id, order.status.value,
                str(order.total), order.created_at,
            )


class StripePaymentGateway(PaymentGateway):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def charge(self, amount: Decimal, token: str) -> str:
        # Call Stripe API
        pass
```

## Dependency Injection (Wiring)

```python
# main.py
async def create_app():
    pool = await asyncpg.create_pool(DATABASE_URL)
    repo = PostgresOrderRepository(pool)
    payment = StripePaymentGateway(os.getenv("STRIPE_KEY"))

    use_case = CreateOrderUseCase(order_repo=repo, payment_gw=payment)

    app = FastAPI()
    app.state.use_case = use_case
    return app

# api.py
@app.post("/orders")
async def create_order(request: CreateOrderRequest):
    use_case: CreateOrderUseCase = request.app.state.use_case
    order = await use_case.execute(
        user_id=request.user_id,
        items=request.items,
    )
    return OrderResponse.from_domain(order)
```

## Testing

```python
# Mock repository
class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._orders: dict[str, Order] = {}

    async def save(self, order: Order) -> None:
        self._orders[order.id] = order

    async def get_by_id(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)


async def test_create_order():
    repo = InMemoryOrderRepository()
    payment = FakePaymentGateway()
    use_case = CreateOrderUseCase(order_repo=repo, payment_gw=payment)

    order = await use_case.execute(
        user_id="user_1",
        items=[{"product_id": "prod_1", "quantity": 2, "price": "10.00"}],
    )

    assert order.status == OrderStatus.CONFIRMED
    assert order.total == Decimal("20.00")
```

## When Clean Architecture is Worth It

- **Complex business logic** with many rules and states
- **Multiple delivery mechanisms** (HTTP, CLI, queue consumer)
- **Long-lived project** (years, not months)
- **Multiple databases** or plans to migrate

## When It is Overkill

- Simple CRUD (use Django or FastAPI directly)
- Prototype or MVP
- Team of one (simplicity wins)
- Short-lived project

The architecture should serve the project, not the other way around.

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written

## Additional Notes

Every pattern requires understanding, not just copying.

### Reflection

Before implementing any pattern, ask yourself:
1. What problem am I solving?
2. Is this the simplest solution?
3. What are the trade-offs?
4. Can the team understand and maintain this?

### Quick Exercise

Write a test for this pattern in your current project.
If its hard to test, the implementation is probably wrong.

### Related Concepts

- Simplicity over complexity
- Solve for today, not for a future that may never come
- Code is read 10x more than it is written
