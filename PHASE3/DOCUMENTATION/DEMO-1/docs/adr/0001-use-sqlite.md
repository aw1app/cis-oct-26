## Title

0001: Use SQLite Instead of PostgreSQL for the Team Directory Service

## Status

Accepted

## Context

The Team Directory service runs as a single instance with a small, low-write
dataset. Writes happen only when a team roster changes. We want no additional
infrastructure to operate.

## Decision

Use SQLite instead of PostgreSQL for the Team Directory service.

## Consequences

SQLite meets the needs of the current single-instance service without additional
infrastructure to operate.

SQLite does not handle concurrent writes from multiple processes well. This
decision must be revisited if the service is scaled to multiple replicas.