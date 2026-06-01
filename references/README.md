# Mega-Coding References

**Complete knowledge base for Principal Engineer-level development.**

---

## Quick Navigation

### By Language
| Language | File | Coverage |
|----------|------|----------|
| Python | `extra/*.md` | Full stack — 50+ reference files |
| Go | `languages/go-patterns.md` | Backend, CLI, concurrency |
| TypeScript | `languages/typescript-patterns.md` | Frontend, Node, type system |
| Rust | `languages/rust-patterns.md` | Systems, performance, async |

### By Topic
| Topic | Files |
|-------|-------|
| **Architecture & Design** | `extra/system-design-reference.md`, `extra/distributed-systems-patterns.md`, `extra/design-patterns-deep-dive.md` |
| **Production Patterns** | `extra/production-patterns.md`, `extra/production-python.md`, `extra/senior-dev-wisdom.md` |
| **Testing** | `extra/testing-strategies.md`, `extra/testing-guide.md`, `extra/testing-advanced.md` |
| **Performance** | `extra/performance-optimization-complete.md`, `extra/speed-optimization.md`, `extra/caching-patterns.md` |
| **Security** | `extra/security-best-practices.md`, `extra/error-handling.md`, `extra/data-validation-patterns.md` |
| **Infrastructure** | `infra/kubernetes-patterns.md`, `infra/kafka-patterns.md`, `extra/cd-deployment-patterns.md` |
| **Leadership** | `principal-engineer-handbook.md`, `extra/senior-dev-wisdom.md`, `extra/learning-path.md` |
| **War Stories** | `battle-scars/production-war-stories.md`, `extra/incident-response.md` |

### By Experience Level
| Level | Recommended Files |
|-------|------------------|
| **Junior** | `extra/clean-code.md`, `extra/idiomatic-python.md`, `error-handling.md`, `SKILL.md` |
| **Middle** | `extra/testing-strategies.md`, `extra/production-patterns.md`, `extra/sqlalchemy-patterns.md` |
| **Senior** | `extra/system-design-reference.md`, `extra/distributed-systems-patterns.md`, `language/*` |
| **Staff/Principal** | `principal-engineer-handbook.md`, `battle-scars/*`, `extra/platform-engineering-patterns.md` |

## Reference Files Overview

### Core Production (50+ files in extra/)

| File | Size | Topics |
|------|------|--------|
| production-patterns.md | 53KB | Connection Pool, Circuit Breaker, Retry, Saga, Feature Flags, Health Checks |
| system-design-reference.md | 55KB | CAP, CQRS, Event Sourcing, Saga, Sharding, Monitoring, Cost Planning |
| python-developer-reference.md | 50KB | Advanced Python, Descriptors, Metaclasses, Concurrency, Async, Optimization |
| testing-strategies.md | 26KB | Async testing, Property-based, Integration, Contract, Load, Mutation |
| principal-engineer-handbook.md | 25KB | Mindset, Architecture, Leadership, SLOs, Incident Response, Strategy |
| performance-optimization-complete.md | 14KB | Profiling, Data Structures, String Ops, Loops, Caching, Async Performance |
| distributed-systems-patterns.md | 14KB | Distributed Lock, Consistent Hashing, Gossip, Bulkhead, 2PC, Tracing |
| system-design-problems.md | 17KB | URL Shortener, Chat, Payment, Netflix, Spanner, Rate Limiter |
| cloud-architecture-patterns.md | 11KB | Multi-Region, Serverless, Microservices, Observability, Cost, DR |
| data-engineering-patterns.md | 12KB | ETL/ELT, Batch, Streaming, Data Quality, Data Lake, Spark |
| platform-engineering-patterns.md | 10KB | IDP, Golden Path, DX, Team Topologies, Internal Developer Loop |
| incident-response.md | 6KB | SEV1 Playbook, Common Patterns, Runbooks, Postmortem Templates |
| cd-deployment-patterns.md | 12KB | Blue-Green, Canary, Rolling, CI/CD, Rollback, Release Checklist |
| data-structures-algorithms-complete.md | 15KB | DS Selection, Algorithm Guide, Complexity Cheatsheet, Implementations |

### Multi-Language (new in v3.0)

| File | Size | Topics |
|------|------|--------|
| languages/go-patterns.md | 13KB | Project Layout, Error Handling, Concurrency, Middleware, Testing |
| languages/typescript-patterns.md | 15KB | Discriminated Unions, Branded Types, FSM, DI, React Hooks |
| languages/rust-patterns.md | 12KB | Error Handling, Tokio, Arena, Newtype, Unsafe, SIMD |

### Infrastructure (new in v3.0)

| File | Size | Topics |
|------|------|--------|
| infra/kubernetes-patterns.md | 9KB | Pod Lifecycle, Resource Mgmt, HPA, Network Policies, Cost |
| infra/kafka-patterns.md | 11KB | Partitioning, Producers, Consumers, Schema Registry, EOS |

### Battle Scars (new in v3.0)

| File | Size | Topics |
|------|------|--------|
| battle-scars/production-war-stories.md | 15KB | 8 real production incidents with code, lessons, and statistics |

## Tips for Reading

1. **Start with SKILL.md** — it's the entry point with quick patterns
2. **Then pick your topic** — use the tables above
3. **Deep dive into extra/*** — each file has production code with battle scars
4. **For new languages** — check languages/ directory
5. **For war stories** — battle-scars/ teaches from real failures
6. **For leadership** — principal-engineer-handbook.md has the full framework

## Contributing

Each reference file follows this structure:
- Title and summary
- Production code examples
- Battle scars (real failures)
- Principal Engineer wisdom
- Key takeaways

*С любовью — команда @intarktelegram*
