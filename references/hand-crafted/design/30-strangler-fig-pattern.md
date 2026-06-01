# Strangler Fig Pattern: Incrementally Replace Legacy Systems

The strangler fig pattern lets you replace a legacy system incrementally,
without a big bang rewrite.

## The Problem

You have a legacy monolith. You want to replace it with microservices.
A rewrite is risky (takes months, might not work).
The strangler fig lets you replace piece by piece.

## How It Works

1. Identify a bounded context in the monolith
2. Build a new service that handles that context
3. Route traffic for that context to the new service
4. Remove the old code from the monolith
5. Repeat until monolith is gone

## Implementation

class StranglerGateway:
    def __init__(self, monolith_url, new_services):
        self.monolith_url = monolith_url
        self.new_services = new_services

    async def route_request(self, request):
        path = request.url.path
        for prefix, service_url in self.new_services.items():
            if path.startswith(prefix):
                return await self.forward_to(service_url, request)

        return await self.forward_to(self.monolith_url, request)

## Example Migration

Phase 1: Extract user management
- Build user-service
- Route /api/users to user-service
- Old code stays in monolith (not called)

Phase 2: Extract order management
- Build order-service
- Route /api/orders to order-service
- Old code stays in monolith

Phase 3: Extract payments
- Build payment-service
- Route /api/payments to payment-service
- Monolith is now only a gateway

## Benefits

1. Continuous delivery - each extraction ships independently
2. Risk reduction - small changes, easy rollback
3. Learning - understand the domain as you extract
4. Gradual migration - no big bang rewrite
5. Parallel running - old and new coexist

## Challenges

1. Data migration - splitting a shared database
2. Transactionality - no ACID across services
3. Latency - new service adds network hop
4. Testing - both old and new paths must work

## When to Use Strangler Fig

- Monolith is too big to rewrite
- You need to deliver value incrementally
- Business cannot tolerate downtime
- You understand the domain boundaries
- You have time for a gradual migration

## When NOT to Use

- The monolith is small (rewrite is faster)
- The monolith is already stable (no need to change)
- You have a hard deadline (rewrite may be simpler)


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.


## Takeaway

Apply one thing today.
