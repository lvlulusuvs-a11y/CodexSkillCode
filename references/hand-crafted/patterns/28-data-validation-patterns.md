# Data Validation Patterns

Validate early, validate often, validate everywhere.

## Layer 1: Input Validation

Validate at the API boundary:

from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)

@app.post("/users")
async def create_user(request: CreateUserRequest):
    # request is validated by Pydantic
    return await user_service.create(request)

## Layer 2: Business Validation

Validate business rules in the service layer:

class OrderService:
    def create(self, data: CreateOrder):
        if not self.inventory.has_stock(data.items):
            raise OutOfStockError()
        if data.total < 0:
            raise ValidationError("total must be positive")
        if self.is_duplicate(data.idempotency_key):
            raise DuplicateError()

## Layer 3: Database Constraints

Last line of defense:

CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    age INTEGER CHECK (age >= 0 AND age <= 150)
);

## Validation Techniques

### 1. Parse, Dont Validate

class Email:
    def __init__(self, value: str):
        if "@" not in value:
            raise ValueError(f"Invalid email: {value}")
        self.value = value

def send_email(email: Email):
    # email is already valid
    ...

### 2. Validation Objects

@dataclass
class ValidatedOrder:
    items: list[ValidatedItem]
    total: Decimal

    @classmethod
    def from_request(cls, request: CreateOrder):
        if not request.items:
            raise ValidationError("order must have items")
        items = [ValidatedItem.from_request(i) for i in request.items]
        total = sum(i.price for i in items)
        return cls(items=items, total=total)

### 3. Rules Engine

rules = [
    Rule("user must be active", lambda u: u.is_active),
    Rule("email must be verified", lambda u: u.email_verified),
    Rule("age must be 18+", lambda u: u.age >= 18),
]

for rule in rules:
    if not rule.check(user):
        raise ValidationError(rule.message)


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.
