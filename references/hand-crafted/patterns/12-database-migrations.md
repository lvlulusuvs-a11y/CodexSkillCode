# Database Migrations: Schema Changes Without Downtime

Migrations separate great engineers from dangerous ones.
A bad migration takes down production. A good one is invisible.

## The Golden Rule

A migration must not break running code. Old code must work with the new schema,
and new code must work with the old schema.

## Safe Changes (No Table Locks)

```sql
-- Add nullable column (instant metadata change)
ALTER TABLE users ADD COLUMN middle_name TEXT;

-- Add index without blocking writes
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Drop index (instant)
DROP INDEX CONCURRENTLY IF EXISTS idx_users_old;

-- Change default (metadata only, no table rewrite)
ALTER TABLE users ALTER COLUMN status SET DEFAULT 'active';

-- Add CHECK constraint (if no validation needed)
ALTER TABLE orders ADD CONSTRAINT ck_positive_amount
    CHECK (amount > 0);
```

These operations dont lock the table. They use fast metadata changes.

## Risky Changes (May Lock Table)

```sql
-- NOT NULL + DEFAULT rewrites EVERY row!
ALTER TABLE users ADD COLUMN full_name TEXT NOT NULL DEFAULT '';
-- On 50M rows: 30 minutes, table locked for writes
```

### Safe Strategy for Adding NOT NULL Columns

```sql
-- Step 1: Add nullable column (instant)
ALTER TABLE users ADD COLUMN full_name TEXT;

-- Step 2: Backfill data in batches (background, non-blocking)
UPDATE users SET full_name = first_name || ' ' || last_name
WHERE full_name IS NULL LIMIT 1000;
-- Repeat this until no more rows

-- Step 3: Set NOT NULL (instant if no NULLs remain)
ALTER TABLE users ALTER COLUMN full_name SET NOT NULL;
```

## Dangerous Changes (Breaking)

```sql
-- RENAME column - breaks old code!
ALTER TABLE users RENAME COLUMN email TO email_address;
-- Old code sends SELECT * and gets email_address -> ERROR

-- DROP column - breaks SELECT * in old code
ALTER TABLE users DROP COLUMN old_field;

-- CHANGE type - table lock, possible data loss
ALTER TABLE users ALTER COLUMN id TYPE BIGINT;
```

## Deployment Strategy

```
Phase 1: Deploy migration (compatible with old code)
  - Add nullable column
  - Create indexes CONCURRENTLY
  - Add new table (if needed)

Phase 2: Deploy code (uses new schema)
  - Now code reads/writes new column
  - Old code ignores it (nullable)

Phase 3: Backfill data (background process)
  - Fill in values for existing rows
  - Batches of 1000 at a time

Phase 4: Finalize schema (next release)
  - Set NOT NULL
  - Drop old columns
  - Drop old indexes
```

## Database per Environment

Each environment has its own database. Never test migrations on production.

```bash
# Migration workflow
make migrate-up         # dev
# Test everything
make migrate-down       # dev
# Fix migration
git commit -m "fix migration"
make migrate-up         # dev
# Now deploy to staging, then production
```

## Rollback Plan

Every migration needs a rollback:

```sql
-- Migration
ALTER TABLE users ADD COLUMN preferences JSONB DEFAULT '{}';

-- Rollback
ALTER TABLE users DROP COLUMN preferences;
```

Test the rollback BEFORE running the migration on production.

## Pre-Migration Checklist

- [ ] Table wont lock (check size: EXPLAIN ANALYZE)
- [ ] New schema works with old running code
- [ ] Old schema works with new deploying code
- [ ] NOT NULL column added correctly (nullable first!)
- [ ] RENAME avoided (its always a breaking change)
- [ ] Rollback migration written and tested
- [ ] Migration runs fast enough (< 1 second typically)

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |

## Additional Practice

Every pattern needs practice to master. Here is a quick exercise.

### Exercise

Take a look at your current project. Find one place where you could apply this pattern.
Write the code. Then ask yourself: is it better now or just different?

### Code Snippet

```python
# Think about this:
def apply_pattern(data):
    """Apply the right pattern for the right problem."""
    if is_simple(data):
        return solve_simple(data)  # Keep it simple
    return solve_with_pattern(data)  # Add complexity when needed
```

### Quick Reference

| Question | Answer |
|----------|--------|
| Does it solve a real problem? | If not, don't use it |
| Is the team familiar with it? | If not, document it |
| Does it add complexity? | Every pattern has a cost |
| Can we remove it later? | If not, rethink |
