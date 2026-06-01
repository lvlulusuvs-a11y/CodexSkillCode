# Pagination: Handling Large Datasets

Every API eventually needs pagination. Here is how I implement it.

## The Problem

```python
# This works for 100 users, kills the server for 1M users
@app.get("/users")
async def get_users():
    return await db.fetch("SELECT * FROM users")
# Memory: 1M users * 1KB = 1GB in memory!
# Network: each user has to be serialized and sent
```

## Cursor-Based Pagination (My Default)

```python
@app.get("/users")
async def get_users(
    cursor: str | None = None,
    limit: int = 20,
):
    # Use the cursor to paginate
    if cursor:
        users = await db.fetch("""
            SELECT id, name, email
            FROM users
            WHERE id > $1
            ORDER BY id
            LIMIT $2
        """, cursor, limit)
    else:
        users = await db.fetch("""
            SELECT id, name, email
            FROM users
            ORDER BY id
            LIMIT $1
        """, limit)

    # Return cursor for next page
    next_cursor = users[-1]["id"] if len(users) == limit else None

    return {
        "data": [dict(user) for user in users],
        "paging": {
            "next_cursor": next_cursor,
            "has_more": next_cursor is not None,
        },
    }
```

**How it works**: Instead of skipping rows (OFFSET), we filter rows after
the last seen ID. The WHERE clause uses the index, so it is O(log n) not O(n).

**Pros**: Fast on any page, stable (new data doesnt shift pages), works with
real-time data.

**Cons**: Cannot jump to a specific page (no "page 5").

### Generic Cursor Function

```python
from dataclasses import dataclass


@dataclass
class Page:
    data: list[dict]
    next_cursor: str | None = None

    def as_dict(self) -> dict:
        result = {"data": self.data}
        if self.next_cursor:
            result["paging"] = {"next": self.next_cursor, "has_more": True}
        return result


async def paginate(
    db,
    table: str,
    columns: list[str],
    cursor_col: str = "id",
    cursor: str | None = None,
    limit: int = 20,
    where: str | None = None,
) -> Page:
    """Generic cursor-based pagination for any table."""

    cols = ", ".join(columns)
    params = []
    query_parts = [f"SELECT {cols} FROM {table}"]

    # WHERE clause
    conditions = []
    if where:
        conditions.append(where)
    if cursor:
        conditions.append(f"{cursor_col} > ${len(params) + 1}")
        params.append(cursor)

    if conditions:
        query_parts.append("WHERE " + " AND ".join(conditions))

    query_parts.append(f"ORDER BY {cursor_col}")
    query_parts.append(f"LIMIT ${len(params) + 1}")
    params.append(limit + 1)  # Fetch one extra to know if there are more

    rows = await db.fetch(" ".join(query_parts), *params)
    has_more = len(rows) > limit
    if has_more:
        rows = rows[:limit]

    next_cursor = rows[-1][cursor_col] if has_more else None
    return Page(data=[dict(r) for r in rows], next_cursor=str(next_cursor) if next_cursor else None)
```

## Offset Pagination (When You Must)

If the UI requires "Page 1, Page 2, Page 3":

```python
@app.get("/users")
async def get_users(page: int = 1, limit: int = 20):
    offset = (page - 1) * limit

    count = await db.fetchval("SELECT COUNT(*) FROM users")
    users = await db.fetch(
        "SELECT * FROM users ORDER BY id LIMIT $1 OFFSET $2",
        limit, offset,
    )

    return {
        "data": [dict(u) for u in users],
        "paging": {
            "page": page,
            "limit": limit,
            "total": count,
            "pages": (count + limit - 1) // limit,
        },
    }
```

**Warning**: OFFSET is O(n). Page 1000 scans 20000 rows before returning results.
Use only for small datasets or admin panels.

## Keyset Pagination

```python
# For compound sorts: "order by status, created_at desc"
@app.get("/orders")
async def get_orders(
    cursor: str | None = None,  # base64 encoded "status:created_at:id"
    limit: int = 20,
):
    if cursor:
        import base64
        decoded = base64.b64decode(cursor).decode()
        status, created_at, last_id = decoded.split(":")

        orders = await db.fetch("""
            SELECT * FROM orders
            WHERE (status, created_at, id) > ($1, $2, $3)
            ORDER BY status, created_at DESC, id
            LIMIT $4
        """, status, created_at, last_id, limit)
    else:
        orders = await db.fetch("""
            SELECT * FROM orders
            ORDER BY status, created_at DESC, id
            LIMIT $1
        """, limit)

    # Encode next cursor
    if orders:
        last = orders[-1]
        cursor_str = f"{last['status']}:{last['created_at']}:{last['id']}"
        next_cursor = base64.b64encode(cursor_str.encode()).decode()
    else:
        next_cursor = None

    return {
        "data": [dict(o) for o in orders],
        "next": next_cursor,
    }
```

## Choosing the Right Strategy

| Strategy | Use Case | Pros | Cons |
|----------|----------|------|------|
| Cursor | Real-time data, large datasets | Fast, stable | Cant jump pages |
| Offset | Admin panels, small tables | Simple, page numbers | Slow on large tables |
| Keyset | Complex sorting | Supports multi-column sort | Complex cursor encoding |

## My Recommendation

Default to cursor-based pagination for all public APIs.
Use offset-based only for admin panels with small datasets (< 10K rows).
Use keyset pagination for complex filtering and sorting scenarios.

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
