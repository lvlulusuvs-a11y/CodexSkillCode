# Monitoring Stack: Prometheus + Grafana

Every service needs a monitoring stack. Here is the standard setup.

## Components

1. Prometheus - metrics collection and storage
2. Grafana - dashboards and visualization
3. Alertmanager - alert routing and notification
4. Node Exporter - server metrics
5. Loki - log aggregation (optional, or use ELK)

## Prometheus Configuration

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "app"
    static_configs:
      - targets: ["localhost:8000"]
    metrics_path: "/metrics"

  - job_name: "node"
    static_configs:
      - targets: ["localhost:9100"]

rule_files:
  - "alerts.yml"

## Alert Rules

groups:
  - name: service_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.instance }}"

      - alert: HighLatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p99 latency over 500ms on {{ $labels.instance }}"

      - alert: ServiceDown
        expr: up{job="app"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"

## Grafana Dashboard

Panels for every service:
1. RPS by endpoint and status
2. Latency heatmap (p50, p95, p99)
3. Error rate
4. CPU and memory usage
5. Active requests
6. Database query duration
7. External API latency
8. Queue size and processing rate

## Alertmanager Configuration

route:
  group_by: ["alertname", "cluster"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: "slack"

receivers:
  - name: "slack"
    slack_configs:
      - api_url: "https://hooks.slack.com/services/..."
        channel: "#alerts"
        title: "{{ .GroupLabels.alertname }}"
        text: "{{ .CommonAnnotations.summary }}"

  - name: "pagerduty"
    pagerduty_configs:
      - routing_key: "..."

## Log Aggregation with Loki

Use Loki for logs if you are already using Grafana.
Use ELK stack if you need advanced search.

loki:
  auth_enabled: false
  common:
    ring:
      kvstore:
        store: inmemory
  schema_config:
    configs:
      - from: 2024-01-01
        store: boltdb-shipper
        object_store: filesystem
        schema: v11


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.


## Practice

Apply one concept from this article.
