# Rust Patterns for Principal Engineers

**Rust в Big Tech: безопасная работа с памятью без GC, fearless concurrency, zero-cost abstractions.**

---

## 1. Error Handling: The Rust Way

### Result + Anyhow for Applications

```rust
use anyhow::{Context, Result};

fn read_user_file(path: &str) -> Result<User> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("failed to read user file: {}", path))?;
    let user: User = serde_json::from_str(&content)
        .with_context(|| format!("failed to parse user from: {}", path))?;
    Ok(user)
}

fn main() -> Result<()> {
    let user = read_user_file("/data/user.json")
        .context("loading user configuration")?;
    println!("User: {}", user.name);
    Ok(())
}

// Output:
// Error: loading user configuration
// Caused by:
//   0: failed to read user file: /data/user.json
//   1: No such file or directory (os error 2)
```

### ThisError для библиотек

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum RepositoryError {
    #[error("user not found: {0}")]
    NotFound(i64),
    #[error("database connection failed: {0}")]
    Connection(#[from] sqlx::Error),
    #[error("validation error: {0}")]
    Validation(String),
    #[error("unknown error")]
    Unknown,
}

// Автоматическая конвертация:
async fn get_user(repo: &UserRepo, id: i64) -> Result<User, RepositoryError> {
    let user = repo.find_by_id(id).await?;  // sqlx::Error конвертится автоматически
    user.ok_or(RepositoryError::NotFound(id))
}
```

---

## 2. Async Patterns: Tokio Best Practices

### Structured Concurrency

```rust
use tokio::sync::Semaphore;

/// Worker pool with bounded concurrency
pub async fn parallel_map<T, R, F>(items: Vec<T>, workers: usize, f: F) -> Vec<R>
where
    T: Send + 'static,
    R: Send + 'static,
    F: Fn(T) -> R + Send + Sync + 'static,
{
    let semaphore = Arc::new(Semaphore::new(workers));
    let mut handles = vec![];

    for item in items {
        let permit = semaphore.clone().acquire_owned().await.unwrap();
        handles.push(tokio::spawn(async move {
            let _permit = permit;
            f(item)
        }));
    }

    let mut results = vec![];
    for handle in handles {
        results.push(handle.await.unwrap());
    }
    results
}
```

### Cancellation Safety

```rust
// ❌ Опасно: select! без cleanup
async fn dangerous() {
    let mut stream = get_stream();
    loop {
        tokio::select! {
            msg = stream.recv() => {
                process(msg).await;
                // если другая ветка побеждает — транзакция зависает
            }
            _ = shutdown_signal() => break,
        }
    }
}

// ✅ Безопасно: Drop-based cleanup
struct Transaction {
    id: String,
    finished: bool,
}

impl Transaction {
    async fn begin() -> Self { /* ... */ }
    async fn commit(&mut self) { self.finished = true; }
}

impl Drop for Transaction {
    fn drop(&mut self) {
        if !self.finished {
            tracing::warn!("Transaction dropped without commit: {}", self.id);
            // автоматический rollback
        }
    }
}

async fn safe_select() {
    let mut tx = Transaction::begin().await;
    tokio::select! {
        _ = process(&mut tx) => tx.commit().await,
        _ = shutdown_signal() => {
            // tx автоматически rollback при drop
        }
    }
}
```

**Battle Scar:** Без cancellation safety теряли данные — при graceful shutdown транзакции зависали в открытом состоянии. Drop-based cleanup гарантирует, что ресурсы освобождаются.

---

## 3. Memory Management: Beyond the Borrow Checker

### Arena Allocation

```rust
use typed_arena::Arena;

struct ASTNode<'arena> {
    kind: NodeKind,
    children: Vec<&'arena ASTNode<'arena>>,
}

fn parse<'arena>(input: &str, arena: &'arena Arena<ASTNode>) -> &'arena ASTNode {
    // Все AST ноды живут в арене — никакого Arc/Box
    arena.alloc(ASTNode {
        kind: NodeKind::Root,
        children: vec![
            arena.alloc(ASTNode {
                kind: NodeKind::Number(42),
                children: vec![],
            })
        ],
    })
}

// zero-cost: все ноды удаляются разом при дропе арены
```

### Cow (Clone-on-Write) для оптимизации

```rust
use std::borrow::Cow;

fn process_name(name: &str) -> Cow<'_, str> {
    if name.contains(' ') {
        // Только при необходимости — аллокация
        Cow::Owned(name.replace(' ', "_"))
    } else {
        // Без аллокации
        Cow::Borrowed(name)
    }
}

// Использование:
let name = "hello world";
let processed = process_name(name);
// Если аллокация не понадобилась — zero overhead
```

---

## 4. Architecture Patterns

### Newtype Pattern

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct UserId(i64);

impl UserId {
    pub fn new(id: i64) -> Result<Self, ValidationError> {
        if id <= 0 {
            return Err(ValidationError::InvalidId(id));
        }
        Ok(Self(id))
    }
}

impl std::fmt::Display for UserId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

// Type-safe: нельзя передать OrderId вместо UserId
fn get_user(id: UserId) -> Result<User, Error>;
fn get_order(id: OrderId) -> Result<Order, Error>;
```

### Repository Pattern with sqlx

```rust
#[derive(Clone)]
pub struct UserRepository<P: PgPool> {
    pool: P,
}

impl<P: PgPool> UserRepository<P> {
    pub async fn find_by_id(&self, id: UserId) -> Result<Option<User>, RepositoryError> {
        let user = sqlx::query_as::<_, User>(
            "SELECT id, name, email, created_at FROM users WHERE id = $1"
        )
        .bind(id.into_inner())
        .fetch_optional(&self.pool)
        .await?;  // автоматическая конвертация через #[from]
        
        Ok(user)
    }
    
    pub async fn create(&self, input: CreateUser) -> Result<User, RepositoryError> {
        if !input.is_valid() {
            return Err(RepositoryError::Validation("invalid input".into()));
        }
        
        let user = sqlx::query_as::<_, User>(
            "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *"
        )
        .bind(&input.name)
        .bind(&input.email)
        .fetch_one(&self.pool)
        .await?;
        
        Ok(user)
    }
}
```

---

## 5. Unsafe: Когда это действительно нужно

```rust
// Не используй unsafe для оптимизации, которую можно сделать безопасно.
// Unsafe нужен для:
// 1. FFI с C-библиотеками
// 2. SIMD инструкции
// 3. Свои аллокаторы
// 4. Реализация безопасной абстракции

// Пример: безопасная обёртка над C API
mod ffi {
    extern "C" {
        pub fn process_data(data: *const u8, len: usize) -> *mut u8;
        pub fn free_result(ptr: *mut u8);
    }
}

pub struct Processor {
    // безопасное API поверх unsafe
}

pub fn process(data: &[u8]) -> Vec<u8> {
    let result = unsafe { ffi::process_data(data.as_ptr(), data.len()) };
    if result.is_null() {
        panic!("process_data returned null");
    }
    let len = unsafe { libc::strlen(result) };
    let output = unsafe {
        let slice = std::slice::from_raw_parts(result, len);
        slice.to_vec()
    };
    unsafe { ffi::free_result(result) };
    output
}
```

---

## 6. Observability: Tracing

```rust
use tracing::{info, error, instrument, Span};
use tracing_subscriber::EnvFilter;

fn setup_tracing() {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::from_default_env())
        .with_target(true)
        .with_thread_ids(true)
        .json()
        .init();
}

#[instrument(skip(repo))]
async fn get_user_handler(
    user_id: UserId,
    repo: UserRepository,
) -> Result<Json<User>, AppError> {
    info!("fetching user");
    
    let user = repo.find_by_id(user_id).await
        .map_err(|e| {
            error!(error = %e, "failed to fetch user");
            AppError::InternalError
        })?;
    
    Ok(Json(user))
}

// В логах:
// {"level":"INFO","target":"myapp::handlers","user_id":"42","message":"fetching user","spans":[{"name":"get_user_handler"}]}
```

---

## 7. Testing: Property-Based Testing

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn reverse_twice_is_identity(input: String) {
        let reversed: String = input.chars().rev().collect();
        let reversed_twice: String = reversed.chars().rev().collect();
        assert_eq!(input, reversed_twice);
    }
    
    #[test]
    fn sort_stable_for_list(mut list: Vec<i32>) {
        let sorted = {
            let mut s = list.clone();
            s.sort();
            s
        };
        
        // sorted всегда отсортирован
        for i in 1..sorted.len() {
            assert!(sorted[i-1] <= sorted[i], "not sorted: {:?}", sorted);
        }
        
        // Все элементы на месте
        list.sort();
        assert_eq!(list, sorted);
    }
}
```

---

## 8. Performance: Zero-Cost Abstractions

### Iterator Pipeline (zero overhead)

```rust
// ❌ С аллокациями
fn process_vec(v: &[i32]) -> Vec<i32> {
    let mut result = Vec::new();
    for &x in v {
        if x > 0 {
            result.push(x * 2);
        }
    }
    result
}

// ✅ Zero-cost: оптимизируется до одного прохода
fn process_iter(v: &[i32]) -> impl Iterator<Item = i32> + '_ {
    v.iter()
        .copied()
        .filter(|&x| x > 0)
        .map(|x| x * 2)
}
```

### SIMD (auto-vectorization)

```rust
// Компилятор автоматически векторизует:
fn sum_array(arr: &[f64]) -> f64 {
    arr.iter().sum()
}

// Ручной SIMD (когда компилятор не справляется):
#[cfg(target_arch = "x86_64")]
use std::arch::x86_64::*;

unsafe fn simd_sum(arr: &[f64]) -> f64 {
    let mut sum = _mm256_setzero_pd();
    for chunk in arr.chunks(4) {
        let vec = _mm256_loadu_pd(chunk.as_ptr());
        sum = _mm256_add_pd(sum, vec);
    }
    let arr: [f64; 4] = std::mem::transmute(sum);
    arr.iter().sum()
}
```

---

## 🧠 Principal Engineer Wisdom for Rust

| Принцип | Почему |
|---------|--------|
| `cargo deny` для зависимостей | Блокирует лицензии с GPL/AGPL для продуктов |
| `cargo audit` в CI | Zero-day уязвимости: знай за час |
| `sccache` для CI сборок | Кэширует скомпилированный код — сборка 10x быстрее |
| `RUSTFLAGS="-C target-cpu=native"` | 10-20% производительности бесплатно |
| Профилируй перед оптимизацией | `cargo flamegraph` или `perf` — не гадай |
| async везде не нужен | Для CPU-bound — threads, для I/O — async |
| `#[derive(Debug, Clone, PartialEq)]` | Стандартные derives — это бесплатная документация |
| Не бойся `.unwrap()` в тестах | В тестах — норм, в продакшене — `?` |

---

## 🔥 Rust в Big Tech: что реально работает

**История из Discord:**  
- Мигрировали критический сервис с Go на Rust  
- Latency p99: 150ms → 25ms (6x улучшение)  
- Memory: 4GB → 128MB  
- Инциденты с out-of-memory: с 3/мес до 0  

**История из Cloudflare:**  
- Pingora (Rust) заменил nginx  
- Connection handling: 10x плотнее  
- CPU: -70%  
- Безопасность типов предотвратила 3 известных класса CVE  

**Но:** Rust не для всего. Прототипы, скрипты, ML — Python. Быстрые итерации — TypeScript.
