## Context

The application has no provider-neutral boundary for external log delivery. See
`proposal.md` for motivation and `specs/pluggable-log-tracking/spec.md` for the
required behavior. Loki's HTTP API accepts JSON at `/loki/api/v1/push` with
stream labels and `[timestamp_ns_as_string, log_line]` values; flat structured
metadata can be a third element in each value tuple.

## Goals / Non-Goals

**Goals:**
- Centralize provider selection behind a small contract so callers do not
  reference a destination-specific client.
- Reuse one HTTP request client and one provider instance per service in a
  process.
- Make Loki local-server delivery correct and configurable without preventing
  future CloudWatch or Google Cloud Logging adapters.

**Non-Goals:**
- Persist logs locally, query Loki, or expose logs through a user-facing API.
- Batch, retry, or asynchronously queue log events in the first release.
- Implement CloudWatch or Google Cloud Logging adapters in this change.

## Decisions

- Define an abstract `BaseLogService` contract for emitting a log event. It
  receives a `LogLevel` enum, message, labels, and flat metadata. A contract is
  preferable to a vendor SDK interface because it keeps callers and future
  providers independent.
- Resolve the configured provider from a dotted class path in Django settings.
  Validate that it subclasses the base contract at startup or first resolution.
  Directly configuring a service enum was rejected because the request requires
  deployments to choose the implementation class.
- Use a lower-level singleton HTTP request client to own session, timeout,
  headers, and request execution. Provider instances consume that client rather
  than creating their own sessions.
- Use a higher-level `LogServiceRegistry` singleton that owns a dictionary from
  `LogService` enum values to initialized provider singletons. This is distinct
  from the configured facade: the facade resolves the selected class, while the
  registry supports explicit service reuse and future multi-service delivery.
- Provide `LogService` values for Grafana Loki, CloudWatch, and Google Cloud
  Logging, and `LogLevel` values for DEBUG, INFO, WARNING, ERROR, and CRITICAL.
  Only the Loki provider is implemented now; other enum values have no
  registered provider until their adapter is added.
- The Loki provider posts `Content-Type: application/json` to the configured
  base URL plus `/loki/api/v1/push`. It creates a string Unix-nanosecond
  timestamp, preserves caller labels as Loki stream labels, serializes level and
  message as the log line, and attaches flat metadata as Loki structured
  metadata. The documented protobuf/Snappy route was rejected because JSON is
  sufficient for the initial local integration and avoids generated bindings.
- Add `pytest-mock` as a test dependency and write unit tests before each
  singleton and provider implementation. Tests will use its `mocker` fixture to
  patch the HTTP transport at the external boundary and to restore patches
  automatically after every test. A full Loki container was rejected because
  deterministic mocked responses meet the no-network requirement.
- Simulate both successful and rejected HTTP responses with `mocker.patch`.
  Assert method, URL, headers, and JSON payload for successful delivery; assert
  the surfaced error context for rejected or transport failures. Reset singleton
  state in test setup so identity assertions prove one HTTP client and one
  provider per service within each test rather than inheriting process state.

## Risks / Trade-offs

- [A configured class is incompatible] -> Validate the base contract before it
  becomes active and raise a clear configuration error.
- [Loki is unavailable or rejects a payload] -> Surface a provider-delivery
  error with status or transport details; callers choose whether to handle it.
- [High-cardinality Loki labels degrade query performance] -> Treat only stable
  dimensions as labels and place per-event fields in structured metadata.
- [Singleton state complicates unit tests] -> Provide an explicit registry reset
  or injection seam limited to test setup.
- [A mock hides an incorrect HTTP request] -> Assert the complete request at
  the transport boundary rather than only the provider return value.

## Migration Plan

No data migration is required. Deploy with the local Loki URL and the Grafana
Loki implementation class configured, then verify a push in Loki/Grafana.
Rollback removes the selected class configuration and logging module usage;
already accepted Loki entries remain external historical data.
