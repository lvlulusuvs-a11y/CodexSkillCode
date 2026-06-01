# Distributed Tracing: End-to-End Visibility

Tracing tracks a request as it flows through multiple services.

## The Problem

In a monolith, you can see the whole request path in one log.
In microservices, a single request touches 5+ services.
Logs are scattered across services. Hard to debug latency.

## How Tracing Works

1. Create a trace ID at the entry point
2. Pass the trace ID through all downstream calls
3. Each service reports spans (operations) with timing
4. Spans are collected and visualized

## Trace Structure

Trace: entire request journey
  Span: work done in one service
    Span: subsystem call (DB query, cache, external API)

Example:
POST /orders (trace_id: abc)
  order-service (span)
    authorize_user (sub-span, 10ms)
    check_inventory (sub-span, 30ms)
      inventory-service (span)
        db_query (sub-span, 25ms)
    process_payment (sub-span, 100ms)
      payment-service (span)
        stripe_api (sub-span, 80ms)
    save_order (sub-span, 20ms)

Total: ~160ms. Bottleneck: payment-service at 100ms.

## OpenTelemetry Setup

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

span_processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://otel-collector:4317")
)
trace.get_tracer_provider().add_span_processor(span_processor)

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

## Manual Instrumentation

@tracer.start_as_current_span("process_payment")
async def process_payment(order_id: str, amount: Money):
    span = trace.get_current_span()
    span.set_attribute("order_id", order_id)
    span.set_attribute("amount", str(amount))

    try:
        result = await payment_gateway.charge(amount)
        span.set_status(trace.StatusCode.OK)
        return result
    except Exception as e:
        span.set_status(trace.StatusCode.ERROR, str(e))
        span.record_exception(e)
        raise

## Propagation

The trace ID must propagate through all services:

Headers:
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
tracestate: vendor1=value1,vendor2=value2

HTTP frameworks propagate automatically.
For queues and async processes, propagate manually:

class TracingMiddleware:
    async def process_message(self, message):
        context = propagate.extract(
            lambda key: message.headers.get(key)
        )
        with trace.use_span(context):
            await self.handle(message)


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.


## Apply

Use one insight from this article.
