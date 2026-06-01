# SOLID Principles: Practical Application

SOLID is not about perfect code. It is about code that doesnt hurt to change.

## Single Responsibility Principle

A class should have one reason to change.

BAD:
class OrderService:
    def create(self, order_data):
        self.validate(order_data)
        order = self.save(order_data)
        self.send_email(order)
        self.update_inventory(order)
        return order

Each responsibility is a reason to change:
- Validation rules change
- Email templates change
- Inventory logic changes

GOOD:
class OrderValidator:
    def validate(self, data): ...

class OrderRepository:
    def save(self, order): ...

class EmailService:
    def send_confirmation(self, order): ...

class OrderService:
    def __init__(self, validator, repo, email, inventory):
        ...
    def create(self, data):
        self.validator.validate(data)
        order = self.repo.save(data)
        self.email.send_confirmation(order)
        await self.inventory.update(order)
        return order

Each class has one reason to change. Test each in isolation.

## Open/Closed Principle

Open for extension, closed for modification.

BAD (modify to extend):
class DiscountCalculator:
    def calculate(self, order, discount_type):
        if discount_type == "percentage":
            return order.total * 0.1
        elif discount_type == "fixed":
            return 10
        elif discount_type == "seasonal":
            return order.total * 0.2

GOOD (extend without modifying):
class DiscountStrategy:
    def apply(self, order): ...

class PercentageDiscount(DiscountStrategy):
    def apply(self, order):
        return order.total * 0.1

class FixedDiscount(DiscountStrategy):
    def apply(self, order):
        return 10

class DiscountCalculator:
    def __init__(self):
        self.strategies = {}
    def register(self, name, strategy):
        self.strategies[name] = strategy
    def calculate(self, order, discount_type):
        strategy = self.strategies.get(discount_type)
        if strategy:
            return strategy.apply(order)
        return 0

## Liskov Substitution Principle

Subtypes must be substitutable for their base types.

BAD:
class Rectangle:
    def set_width(self, w): self.width = w
    def set_height(self, h): self.height = h
    def area(self): return self.width * self.height

class Square(Rectangle):
    def set_width(self, w):
        self.width = w
        self.height = w  # violates LSP!

Square is not a substitute for Rectangle.
Client setting different width and height breaks.

GOOD: Separate interface:
class Shape:
    def area(self): ...

class Rectangle(Shape): ...
class Square(Shape): ...

## Interface Segregation

Clients should not depend on interfaces they dont use.

BAD:
class Worker:
    def work(self): ...
    def eat(self): ...
    def sleep(self): ...

GOOD:
class Workable:
    def work(self): ...
class Eatable:
    def eat(self): ...
class Sleepable:
    def sleep(self): ...

## Dependency Inversion

Depend on abstractions, not concretions.

BAD:
class OrderService:
    def __init__(self):
        self.db = PostgreSQL()  # concrete dependency

GOOD:
class OrderService:
    def __init__(self, db: Database):  # abstract dependency
        self.db = db


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.


## Takeaway

Apply one thing from this.
