# 🔥 Военные истории из окопов продакшена

Это не выдумки. Это то, через что я прошёл. Каждая история — шрам.

## История 1: Connection Pool, который убил сервис

**Время**: 3:00 AM, воскресенье
**Симптом**: Сервис не отвечает. Вообще. healthcheck — 500.
**Нагрузка**: Обычная, ~100 rps

Диагностика:
```
curl http://service:8080/health
→ timeout через 30 секунд

kubectl logs pod/my-service-xxx | tail
→ нет ошибок, просто тишина

curl http://service:9090/metrics | grep db
db_connections_open 50
db_connections_idle 0
db_connection_errors 50
```

Все 50 соединений в pool заняты. Ни одно не возвращается.

**Причина:**
```python
# Наш код
async def handle_request(request):
    user = await db.fetch("SELECT * FROM users WHERE id = $1", request.user_id)
    result = await process_with_external_api(user, request.data)  
    # ⚡ External API не отвечает (timeout 60s)
    # ⚡ Пока мы ждём — соединение с БД держится!
    await db.execute("UPDATE users SET last_seen = NOW() WHERE id = $1", request.user_id)
    return result
```

Когда external API лёг, все 50 обработчиков зависли в ожидании. Через 60 секунд они упали по таймауту, но соединения не вернулись в pool — потому что `release()` не был вызван (исключение прервало выполнение).

**Фикс:**
```python
# Всегда используем контекстный менеджер
async def handle_request(request):
    async with db.acquire() as conn:  # Гарантированный return
        user = await conn.fetch(...)
        result = await process_with_external_api(user, request.data)
        await conn.execute(...)
        return result
```

**Урок:** Любой `await` между acquire и release — потенциальная точка отказа. Если она упадёт — соединение потеряно. Используй контекстные менеджеры для всех ресурсов.

**Что изменили:**
- Connection pool мониторинг (использование, ожидание, ошибки)
- Все `acquire` через контекстные менеджеры
- Timeout на внешние API (5s вместо 60s)
- Bulkhead для external API (не блокируем DB pool)

## История 2: Async, который оказался sync

**Симптом**: Под нагрузкой 500 rps latency p99 прыгает с 50ms до 10s

**Диагностика:**
```python
# Код, который казался асинхронным
@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    user_data = db.query(User).filter(User.id == user_id).first()  
    # ⚡ Это sync! SQLAlchemy 1.x ORM sync session!
    return UserSchema.from_orm(user_data)
```

Весь код был обёрнут в `async def`, но внутри использовал синхронный SQLAlchemy. 
Каждый запрос блокировал event loop на 20-50ms. При 500 rps — очередь накапливалась, latency росла.

**Фикс:**
```python
# Async SQLAlchemy 2.0
@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    async with async_session() as session:
        user_data = await session.get(User, user_id)
    return UserSchema.from_orm(user_data)
```

**Урок:** `async def` не делает код асинхронным. Асинхронным его делает `await`. Если внутри `async def` есть синхронный I/O — это синхронный код с приставкой async.

## История 3: Retry Storm, или как 3 сервиса убили друг друга

**Время**: 2:00 PM, четверг
**Симптом**: Все три сервиса лежат. CPU 100%, memory 100%, но запросов почти нет.

**Что произошло:**

Сервис A → (запрос) → Сервис B → (запрос) → Сервис C

Сервис C начал тормозить (проблема с БД). 
Сервис B настроил retry с timeout 1s.
Сервис A тоже настроил retry.

```
Сервис A: шлёт запрос → timeout 1s → retry → timeout → retry → ...
Сервис B: получает запрос → ждёт Сервис C → timeout → retry → ...
Сервис C: получает кучу запросов → ещё медленнее → ещё больше retry
```

Петля положительной обратной связи. Retry только усугубляет проблему.

**Фикс:**
```python
# 1. Circuit breaker
# 2. Jitter на retry (не все одновременно)
# 3. Max retries = 2
# 4. Client-side timeout меньше server-side timeout
@retry(max_attempts=2, base_delay=1.0, jitter=0.2)
async def call_service_b():
    async with asyncio.timeout(2.0):  # Client timeout = 2s
        return await client.post(SERVICE_B_URL, timeout=5.0)  # Server timeout = 5s
```

**Урок:** Retry без jitter и circuit breaker — это оружие массового поражения. Нагрузка, которую генерируют ретраи, часто убивает систему быстрее оригинальной проблемы.

## История 4: Миграция БД, которая снесла прод

**Время**: 11:00 AM, вторник
**Симптом**: Все запросы к БД встали. Полная остановка.

**Что произошло:**
```sql
-- Миграция на большую таблицу (50M записей)
ALTER TABLE orders ADD COLUMN discount_amount DECIMAL;

-- ❌ PostgreSQL должен просканировать всю таблицу, 
--    чтобы заполнить колонку дефолтным NULL
--    (на самом деле нет — это metadata-only, но:)

ALTER TABLE orders ADD COLUMN discount_amount DECIMAL NOT NULL DEFAULT 0;
-- ❌ А вот ЭТО блокирует всю таблицу на 35 минут!
--    PostgreSQL переписывает каждую страницу, чтобы записать 0
```

Блокировка на 35 минут. Все запросы, которые пишут в `orders` — встали. 
Очередь накапливается. Сервисы падают по timeout. Soutage.

**Правильный вариант:**
```sql
-- 1. Добавить колонку с nullable (мгновенно)
ALTER TABLE orders ADD COLUMN discount_amount DECIMAL;

-- 2. Заполнить в фоне (пачками по 1000)
UPDATE orders SET discount_amount = 0 
WHERE discount_amount IS NULL 
LIMIT 1000;
-- Повторять, пока не закончится

-- 3. Сделать NOT NULL
ALTER TABLE orders ALTER COLUMN discount_amount SET NOT NULL;
```

**Урок:** Любая миграция на больших таблицах — потенциальный даунтайм. 
Знай свою БД. Знай её блокировки. И никогда не делай `NOT NULL DEFAULT` на большой таблице.

## История 5: Race condition, который жил месяц

**Симптом**: Редко (1 из 10000) заказы создаются дважды с одинаковым payment_id

**Причина:**
```python
async def create_order(user_id: str, payment_id: str):
    # Проверка — не было ли уже такого платежа
    existing = await db.fetchrow(
        "SELECT id FROM orders WHERE payment_id = $1", payment_id
    )
    if existing:
        raise DuplicateOrderError()
    
    # Гонка! Два запроса одновременно прошли проверку
    # Теперь оба создадут заказ с одинаковым payment_id
    order = await db.fetchrow(
        "INSERT INTO orders (user_id, payment_id) VALUES ($1, $2) RETURNING *",
        user_id, payment_id,
    )
    return order
```

**Фикс:**
```python
async def create_order(user_id: str, payment_id: str):
    # UNIQUE constraint + ON CONFLICT — атомарная операция
    order = await db.fetchrow("""
        INSERT INTO orders (user_id, payment_id) 
        VALUES ($1, $2) 
        ON CONFLICT (payment_id) DO NOTHING
        RETURNING *
    """, user_id, payment_id)
    
    if not order:
        raise DuplicateOrderError(f"Payment {payment_id} already processed")
    return order
```

Со `UNIQUE` индексом на `payment_id` гонка невозможна: первый запрос вставит, второй — получит конфликт.

**Урок:** Check-then-act — классическая гонка. В БД используй unique constraints и `ON CONFLICT`. В коде — блокировки. Никогда не полагайся на проверку перед записью.

## Что я вынес из всех этих историй

1. **Контекстные менеджеры** для всех ресурсов (соединения, файлы, блокировки)
2. **Timeouts** на все внешние вызовы (никогда не жди бесконечно)
3. **Circuit breaker** для всех external dependencies
4. **Jitter** на все retry (никто не ретраит одновременно)
5. **Unique constraints** для всех бизнес-ключей (защита от гонок)
6. **Мониторинг** всех pool'ов (соединения, goroutines, connections)
7. **Каждый async вызов** — потенциальная точка отказа
8. **Read-only транзакции** там, где пишем только читаем
9. **Ручные миграции** с EXPLAIN ANALYZE на большой таблице
10. **Post-mortem после каждого инцидента** (иначе баг вернётся)

---

**Суть**: Production — это место, где теории встречаются с реальностью. И реальность всегда побеждает.
