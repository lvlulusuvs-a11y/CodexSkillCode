# Refactoring Recipes: Safe Code Changes

Refactoring is changing code without changing behavior.
Done right, it improves code quality. Done wrong, it breaks production.

## Safe Refactoring Workflow

1. Write tests that cover the behavior
2. Make small, atomic changes
3. Run tests after each change
4. Keep changes under 30 minutes each
5. Commit after each safe step

## Recipe 1: Extract Method

When a function does too much:

def send_invoice(user_id: str, order_id: str):
    user = db.get_user(user_id)
    order = db.get_order(order_id)
    total = calculate_total(order)
    email_body = format_invoice(user, order, total)
    email_service.send(user.email, "Your Invoice", email_body)
    order.status = "invoiced"
    db.save(order)

Extract into smaller methods:

def send_invoice(user_id: str, order_id: str):
    user = load_user(user_id)
    order = load_order(order_id)
    email = build_invoice_email(user, order)
    send_email(user.email, email)
    mark_as_invoiced(order)

def load_user(user_id: str) -> User:
    return db.get_user(user_id)

def build_invoice_email(user: User, order: Order) -> str:
    total = calculate_total(order)
    return format_invoice(user, order, total)

def send_email(email: str, body: str):
    email_service.send(email, "Your Invoice", body)

def mark_as_invoiced(order: Order):
    order.status = "invoiced"
    db.save(order)

## Recipe 2: Rename Variable

A variable name should explain what it holds.

BAD:
def calc(a, b, c):
    return a * (b - c)

GOOD:
def calculate_discounted_price(base_price, discount_rate, tax):
    return base_price * (discount_rate - tax)

Modern IDEs make renaming safe and easy. Use this power.

## Recipe 3: Replace Conditional with Polymorphism

Instead of if/else chains, use classes.

BEFORE:
def calculate_shipping(order, method):
    if method == "standard":
        return order.weight * 0.5
    elif method == "express":
        return order.weight * 1.5
    elif method == "overnight":
        return order.weight * 3.0

AFTER:
class StandardShipping:
    def calculate(self, order):
        return order.weight * 0.5

class ExpressShipping:
    def calculate(self, order):
        return order.weight * 1.5

strategies = {
    "standard": StandardShipping(),
    "express": ExpressShipping(),
}

def calculate_shipping(order, method):
    return strategies[method].calculate(order)

## Recipe 4: Introduce Parameter Object

When a function has too many parameters:

def create_user(name, email, password, role, is_active, notify):
    ...

@dataclass
class CreateUserRequest:
    name: str
    email: str
    password: str
    role: str = "user"
    is_active: bool = True
    notify: bool = False

def create_user(request: CreateUserRequest):
    ...

## Recipe 5: Split Loop

When one loop does multiple things:

for user in users:
    send_email(user)
    generate_report(user)
    update_cache(user)

Split into separate loops, one responsibility each:

for user in users:
    send_email(user)

for user in users:
    generate_report(user)

for user in users:
    update_cache(user)

## Recipe 6: Replace Nested Conditional with Guard Clauses

def process_order(order):
    if order.is_valid:
        if order.has_stock:
            if order.payment_ok:
                confirm(order)
                send_notification(order)
            else:
                fail(order, "payment")
        else:
            fail(order, "stock")
    else:
        fail(order, "validation")

def process_order(order):
    if not order.is_valid:
        return fail(order, "validation")
    if not order.has_stock:
        return fail(order, "stock")
    if not order.payment_ok:
        return fail(order, "payment")
    confirm(order)
    send_notification(order)

## When NOT to Refactor

1. Code that works and isnt being changed
2. Code that will be replaced soon
3. Third-party code you shouldnt modify
4. Performance-critical code without benchmarks
5. Friday afternoon before a deadline


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.
