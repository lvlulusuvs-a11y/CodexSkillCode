# Multi-Language Support Index

**Mega-Coding now supports development in 4 languages across the full stack.**

---

## Supported Languages

| Language | Reference | Stack Coverage |
|----------|-----------|---------------|
| **Python** | `references/extra/` | Backend, APIs, data, ML, infra |
| **Go** | `references/languages/go-patterns.md` | Backend, microservices, CLI |
| **TypeScript** | `references/languages/typescript-patterns.md` | Frontend, backend (Node.js) |
| **Rust** | `references/languages/rust-patterns.md` | Systems, performance-critical |

## Infrastructure Support

| Technology | Reference | Coverage |
|------------|-----------|----------|
| **Kubernetes** | `references/infra/kubernetes-patterns.md` | Deploy, scaling, networking |
| **Kafka** | `references/infra/kafka-patterns.md` | Event streaming, pipelines |
| **Docker** | `assets/boilerplate-docker-compose.md` | Containerization |
| **CI/CD** | `references/extra/ci-cd-patterns.md` | Pipelines, automation |

## Cross-Cutting Patterns (Language-Agnostic)

| Pattern | Reference |
|---------|-----------|
| System Design | `references/extra/system-design-reference.md` |
| Distributed Systems | `references/extra/distributed-systems-patterns.md` |
| Production Patterns | `references/extra/production-patterns.md` |
| Battle Scars | `references/battle-scars/production-war-stories.md` |
| Principal Handbook | `references/principal-engineer-handbook.md` |

## Quick Start by Language

```bash
# Python project
mega init --type fastapi

# Go project
# Create from template:
mkdir my-service && cd my-service
go mod init my-service
# See references/languages/go-patterns.md

# TypeScript project
npx create-next-app my-app
# See references/languages/typescript-patterns.md

# Rust project
cargo init my-crate
# See references/languages/rust-patterns.md
```
