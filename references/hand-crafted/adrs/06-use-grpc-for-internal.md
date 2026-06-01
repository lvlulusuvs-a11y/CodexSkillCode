# ADR 006: Use gRPC for Internal Service Communication

Status: Accepted

## Context

We need an efficient protocol for internal service-to-service communication.
Requirements: low latency, strong typing, streaming support.

## Decision

Use gRPC for all internal microservice communication.

## Rationale

1. Protocol Buffers - strongly typed contracts
2. HTTP/2 - multiplexed streams, lower overhead
3. Streaming - unary, server streaming, client streaming, bidirectional
4. Code generation - clients and servers from .proto files
5. Performance - 5-10x faster than JSON REST
6. Tooling - reflection, health checking, load balancing

## Protocol Buffers Schema

syntax = "proto3";

package order;

service OrderService {
  rpc GetOrder (GetOrderRequest) returns (Order);
  rpc ListOrders (ListOrdersRequest) returns (ListOrdersResponse);
  rpc CreateOrder (CreateOrderRequest) returns (Order);
  rpc StreamOrders (StreamOrdersRequest) returns (stream Order);
}

message Order {
  string id = 1;
  string user_id = 2;
  repeated OrderItem items = 3;
  double total = 4;
  string status = 5;
  string created_at = 6;
}

## Consequences

Positive:
- Fast, typed, streaming-capable
- Automatic client generation
- Stronger contracts than REST + JSON

Negative:
- More setup than REST
- Protocol Buffers learning curve
- Debugging harder (binary format)
- Browser support limited


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.


## Apply

One insight per day.
