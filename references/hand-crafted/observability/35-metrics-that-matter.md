# Metrics That Matter: What to Track

Not all metrics are useful. Here is what I track.

## RED Method (Services)

Rate - requests per second
Errors - failed requests per second
Duration - latency distribution

For every service, every endpoint.

## USE Method (Infrastructure)

Utilization - how full is the resource?
Saturation - how much extra work is queued?
Errors - how many errors?

For every resource: CPU, memory, disk, network.

## Four Golden Signals

1. Latency - time to service a request
2. Traffic - demand on the system
3. Errors - rate of failed requests
4. Saturation - how full the service is

## Business Metrics

Not just technical:

1. Active users
2. Conversion rate
3. Revenue per user
4. Response time SLA compliance
5. Feature adoption rate
6. Error rate by feature

## What to Alert On

Alert on symptoms, not causes:

Bad alert: "CPU > 80%" (cause, user may not notice)
Good alert: "p99 latency > 500ms" (symptom, user notices)

Bad alert: "Database connection errors" (cause)
Good alert: "Error rate > 1%" (symptom)

## Metric Granularity

1. Per service - is it working?
2. Per endpoint - which endpoint is slow?
3. Per user - which users are affected?
4. Per instance - which instance is failing?

## Dashboard Structure

Row 1: Overview (RPS, latency, errors)
Row 2: Service health (RED metrics per service)
Row 3: Infrastructure (CPU, memory, disk)
Row 4: Business metrics (users, revenue, conversion)
Row 5: Dependencies (DB, cache, queue)
Row 6: Top-N lists (slowest endpoints, top errors)

## Prometheus Recording Rules

Record expensive queries:

rules:
  - record: service:http_requests:rate5m
    expr: rate(http_requests_total[5m])

  - record: service:http_request_duration:p99_5m
    expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.


## Practice

Apply one concept from this.
