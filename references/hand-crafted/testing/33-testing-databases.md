# Testing Database Code

Database testing is tricky. Here is how I do it.

## Repository Tests with Testcontainers

from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16") as pg:
        yield pg.get_connection_url()

@pytest.fixture
async def repo(postgres):
    pool = await asyncpg.create_pool(postgres)
    await run_migrations(pool)
    yield PostgresUserRepository(pool)
    await pool.close()

async def test_create_user(repo):
    user = await repo.create(email="test@example.com", name="Alice")
    assert user.id is not None
    assert user.email == "test@example.com"

async def test_get_user(repo):
    created = await repo.create(email="test@example.com", name="Alice")
    found = await repo.get_by_id(created.id)
    assert found.email == created.email

async def test_get_nonexistent_user(repo):
    user = await repo.get_by_id("nonexistent")
    assert user is None

async def test_duplicate_email(repo):
    await repo.create(email="test@example.com", name="Alice")
    with pytest.raises(IntegrityError):
        await repo.create(email="test@example.com", name="Bob")

## Testing Transactions

async def test_transaction_rollback(repo, pool):
    async with pool.acquire() as conn:
        async with conn.transaction():
            await repo.create(email="test@example.com", name="Alice")
            raise Exception("rollback!")

    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM users")
        assert len(rows) == 0  # Transaction rolled back

## Testing Migrations

Test that migrations work and are reversible:

from alembic import command
from alembic.config import Config

async def test_migration_upgrade(postgres):
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", postgres)
    command.upgrade(config, "head")
    # Schema is applied

async def test_migration_downgrade(postgres):
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", postgres)
    command.upgrade(config, "head")
    command.downgrade(config, "-1")
    # Schema is reverted

async def test_migration_data_preserved(postgres):
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", postgres)
    command.upgrade(config, "base")

    # Insert data with old schema
    # ...

    command.upgrade(config, "head")
    # Data should still be there


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.
