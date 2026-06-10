$ python supervisor.py

The orchestrator calls three architects, then hands off to the visualizer.

============================================================
# Architectural Designs: Request Storage for Retry on Failure

## 1. SQL-Based Recoverable Request Storage

```mermaid
graph TD
    A[API Gateway] --> B[Request Service]
    B --> C[SQL Database]
    C --> D{Error Handling}
    D -->|Success| E[Complete Request]
    D -->|Fail| F[Retry Service]
    F --> G[Dead Letter Queue]
    F --> C
    B --> H[Logging & Metrics]
    B --> I[Monitoring]
    I --> J[Health Check & Alerts]
```

**Key features:** Idempotency via payload hashing, backpressure with priority
queuing, circuit breaker resilience, `SKIP LOCKED` for concurrent batch processing.

## 2. NoSQL-Based Request Storage

```mermaid
graph TD
    A[Client Layer] --> B[Request Service]
    B --> C[NoSQL Database]
    C --> D[Retry Service]
    D -->|Retry| C
    D --> G[Logging & Metrics]
    G --> H[Monitoring & Alerts]
    A --> I[API Gateway]
```

**Key features:** Flexible schemas for varying request shapes, async event-driven
decoupling, scalable at the cost of transactional guarantees.

## 3. Hybrid Architecture

```mermaid
graph TD
    A[API Gateway] --> B[Request Service]
    B --> C[NoSQL Database]
    B --> D[SQL Database]
    C --> E[Request Metadata]
    D --> F[Processing Outcome]
    E --> G[Retry Service]
    G -->|Retry| C
    G -->|Process| D
    H[Monitoring] --> B
```

**Key features:** NoSQL for request metadata (flexible ingestion), SQL for
processing outcomes (strong consistency), best of both worlds.
============================================================
