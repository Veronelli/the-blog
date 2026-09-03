## Purpose

The Swagger docs capability generates and serves the OpenAPI schema document (JSON/YAML) for the project's API surface, enabling developer discovery during local development while keeping the schema endpoint hidden in production.

## ADDED Requirements

### Requirement: OpenAPI schema is generated from DRF
The system MUST generate a valid OpenAPI schema from the project's DRF views, viewsets, and serializers.

#### Scenario: Schema endpoint returns OpenAPI document
- **WHEN** a developer requests the OpenAPI schema endpoint in development
- **THEN** the system returns a JSON or YAML document conforming to the OpenAPI specification

### Requirement: OpenAPI schema endpoint is disabled in production
The system MUST NOT expose the OpenAPI schema endpoint when running in production mode.

#### Scenario: Production hides the OpenAPI schema
- **WHEN** a request is made to the OpenAPI schema path with `DEBUG=False`
- **THEN** the system returns a 404 response

### Requirement: OpenAPI tooling is a development dependency
The system MUST declare the OpenAPI generator package as a development dependency only.

#### Scenario: Production install excludes OpenAPI tooling
- **WHEN** the project's dependencies are installed for production without development extras
- **THEN** the OpenAPI generator package is not installed
