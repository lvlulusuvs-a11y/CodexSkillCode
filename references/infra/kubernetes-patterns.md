# Kubernetes Patterns for Principal Engineers

**Не просто манифесты — паттерны эксплуатации продакшен-кластеров.**

---

## 1. Pod Lifecycle: Graceful Shutdown

### PreStop Hook

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    lifecycle:
      preStop:
        exec:
          command:
          - /bin/sh
          - -c
          - |
            # Уведомить service discovery о shutdown
            curl -X POST http://localhost:9090/-/deregister || true
            # Дать время завершить текущие запросы
            sleep 5
    terminationGracePeriodSeconds: 60
```

**Battle Scar:** Без preStop при rolling update теряли 5-10% запросов — pod удалялся, пока обрабатывал active requests. 100% запросов стали успешными после внедрения.

### startupProbe + livenessProbe + readinessProbe

```yaml
readinessProbe:      # готов принимать трафик
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10

livenessProbe:       # жив ли процесс (restart if dead)
  httpGet:
    path: /health/live
    port: 8080
  periodSeconds: 30
  failureThreshold: 3

startupProbe:        # для медленно стартующих приложений
  httpGet:
    path: /health/startup
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 30  # 150 секунд на старт
```

**Зачем:** livenessProbe без startupProbe убивает контейнеры, которые долго инициализируются (Java, ML модели).

---

## 2. Resource Management

### Requests & Limits: Почему не 1:1

```yaml
# ❌ Не делай requests == limits — OOMKill при скачках
resources:
  requests:
    cpu: "1"
    memory: "1Gi"
  limits:
    cpu: "2"       # может использовать burst, если CPU свободен
    memory: "2Gi"  # защита от memory leak

# ✅ QoS Guaranteed (for critical services)
resources:
  requests:
    cpu: "2"
    memory: "4Gi"
  limits:
    cpu: "2"
    memory: "4Gi"

# Vertical Pod Autoscaler recommendations:
# VPA анализирует usage и предлагает оптимальные requests
```

**Battle Scar:** Установили requests == limits для всех сервисов — кластер использовал 40% ресурсов, а платили за 100%. После внедрения burstable классов — utilisation поднялась до 85%.

### Pod Disruption Budgets

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 2          # ИЛИ maxUnavailable: 1
  selector:
    matchLabels:
      app: my-app
```

**Без PDB:** node drain может убить все реплики = downtime.  
**С PDB:** гарантирует, что хотя бы N реплик всегда работают.

---

## 3. Config & Secrets Management

### External Secrets Operator

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-secret
spec:
  refreshInterval: "1h"
  secretStoreRef:
    kind: SecretStore
    name: aws-secrets-manager
  target:
    name: database-creds
    creationPolicy: Owner
  data:
    - secretKey: password
      remoteRef:
        key: /prod/database/password
```

**Почему:** Хранить секреты в git (даже зашифрованные) — это компромисс. AWS Secrets Manager / HashiCorp Vault — source of truth.

---

## 4. Advanced Scheduling

### Pod Topology Spread Constraints

```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: my-app
    - maxSkew: 1
      topologyKey: kubernetes.io/hostname
      whenUnsatisfiable: ScheduleAnyway
```

**Без этого:** 5 подов могут оказаться на одной ноде/в одной зоне. При падении ноды — потеря 5 реплик разом.

---

## 5. Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 3
  maxReplicas: 30
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300   # не скейлить вниз резко
      policies:
        - type: Percent
          value: 10                     # не больше 10% в минуту
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0      # скейлить вверх быстро
      policies:
        - type: Percent
          value: 100                     # удвоение за минуту
          periodSeconds: 60
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

**Battle Scar:** Без stabilizationWindowSeconds HPA дёргался туда-сюда при скачках нагрузки — создавал и удалял поды каждые 2 минуты. После настройки — стабильно.

---

## 6. Cost Optimization

| Стратегия | Экономия | Сложность |
|-----------|----------|-----------|
| Spot instances (для stateless) | 60-90% | Средняя |
| Cluster Autoscaler | 20-40% | Низкая |
| Right-sizing (VPA + анализ) | 30-50% | Низкая |
| Remove unused resources | 10-20% | Средняя |
| Graviton/ARM инстансы | 20-30% | Низкая |
| HPA с custom metrics | 20-40% | Высокая |

**Battle Scar:** В 2023 оптимизировали кластер AWS EKS:  
- Spot instances для staging: -83% cost  
- Right-sizing: -35% cost  
- Graviton migration: -25% cost  
- Итого: с $120K/мес до $45K/мес

---

## 7. Observability Stack

### OpenTelemetry Operator

```yaml
apiVersion: opentelemetry.io/v1alpha1
kind: OpenTelemetryCollector
metadata:
  name: otel-collector
spec:
  config: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
    exporters:
      prometheus:
        endpoint: 0.0.0.0:8889
      otlp:
        endpoint: "jaeger-collector:4317"
        tls:
          insecure: true
    service:
      pipelines:
        traces: [receivers: [otlp], exporters: [otlp]]
        metrics: [receivers: [otlp], exporters: [prometheus]]
```

**Правило:** 3 pillars observability → Logs + Metrics + Traces.  
Без трейсов ты не найдёшь, где latency в распределённой системе.

---

## 8. Network Policies: Микросегментация

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-allow-frontend
spec:
  podSelector:
    matchLabels:
      app: api
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - port: 8080
```

**Без NetworkPolicy:** любой под в кластере может достучаться до любого сервиса.  
**С NetworkPolicy:** явное разрешение трафика — безопасность по умолчанию.

---

## 🧠 Principal Engineer Wisdom for Kubernetes

| Правило | Почему |
|---------|--------|
| Используй `kubectl` через `k9s` | Productivity + визуальный дашборд |
| Всегда `readOnlyRootFilesystem: true` | Безопасность + stateless |
| `securityContext.runAsNonRoot: true` | Безопасность |
| PDB обязателен для production | Иначе node drain = downtime |
| PodAntiAffinity для критических сервисов | Не класть все яйца в одну корзину |
| `requests.memory` не равны `limits.memory` | OOMKill меньше, utilisation выше |
| Service Mesh (Istio/Linkerd) только если >20 микросервисов | Overhead для маленьких кластеров |
| Managed Kubernetes (EKS/GKE/AKS) > self-hosted | TCO + меньше инцидентов |

---

## 🔥 Kubernetes в Big Tech: что реально работает

**История:** Миграция 200 микросервисов на EKS в 2022-2023.

| Метрика | До (EC2) | После (EKS) |
|---------|----------|-------------|
| Time to deploy | 30 мин | 3 мин |
| Rollback | 20 мин | 30 сек |
| Resource utilisation | 35% | 78% |
| Cost per service | $500/мес | $180/мес |
| Incidents/month | 15 | 3 |
| MTTR | 2 часа | 25 мин |
