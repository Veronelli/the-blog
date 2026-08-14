## 1. Logging Contracts and Configuration

- [ ] 1.1 Add `pytest-mock` as a test dependency and configure the `mocker` fixture for the logging tests.
- [ ] 1.2 Write unit tests for configured implementation resolution and invalid configuration before implementing the logging contract.
- [ ] 1.3 Create the logging module with `LogService` and `LogLevel` enums and the abstract base service contract.
- [ ] 1.4 Add Django settings for the selected implementation class and local Loki connection values; validate that the configured class satisfies the contract.

## 2. Singleton Infrastructure

- [ ] 2.1 Write unit tests proving repeated resolution reuses one HTTP client, each registered service has one provider instance, and multiple services do not duplicate instances.
- [ ] 2.2 Implement the reusable HTTP request singleton with session, timeout, headers, and error handling.
- [ ] 2.3 Implement the higher-level log-service registry singleton that maps service enums to service instances and reuses them.
- [ ] 2.4 Add a test-only singleton reset or injection seam so unit tests remain isolated.

## 3. Grafana Loki Provider

- [ ] 3.1 Write unit tests with `mocker.patch` for the configured Loki provider using mocked HTTP success, rejection, and transport-failure responses; assert the complete outbound request and prevent network access.
- [ ] 3.2 Implement the Grafana Loki service using the base contract and the HTTP request singleton.
- [ ] 3.3 Serialize level, message, labels, flat metadata, and a string Unix-nanosecond timestamp into the Loki `POST /loki/api/v1/push` JSON payload.

## 4. Verification

- [ ] 4.1 Run focused logging tests and `uv run python project/manage.py check`.
- [ ] 4.2 Verify the unit test suite covers mocked successful, rejected, and transport-failure responses without allowing outbound network requests.
