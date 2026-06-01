# ADR 009: Use pytest Over unittest

Status: Accepted

## Context

We need a testing framework that is concise, powerful, and well-supported.
The standard library unittest is verbose and less flexible.

## Decision

Use pytest for all Python testing.

## Rationale

1. Concise syntax - no classes, no self.asserts
2. Powerful fixtures - dependency injection for tests
3. Plugin ecosystem - coverage, async, mock
4. Auto-discovery - no test suite configuration
5. Parametrization - test multiple inputs easily
6. Assertion introspection - detailed failure messages
7. Compatible with unittest - existing tests still work

## Key Features

Fixtures:
@pytest.fixture
async def db():
    pool = await create_pool()
    yield pool
    await pool.close()

Parametrize:
@pytest.mark.parametrize("input,expected", [
    (1, 2), (2, 4), (3, 6),
])
def test_double(input, expected):
    assert double(input) == expected

Mocks:
async def test_service(mocker):
    mock_repo = mocker.AsyncMock()
    mock_repo.get.return_value = User(id="1")


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.
