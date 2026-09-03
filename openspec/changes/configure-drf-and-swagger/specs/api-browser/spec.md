## Purpose

The API browser capability exposes DRF's interactive browsable API and endpoint listing so developers can discover and test endpoints during local development without exposing that interface in production.

## ADDED Requirements

### Requirement: Browsable API is available in development
The system MUST expose DRF's browsable API and API root listing when the application runs in development mode.

#### Scenario: Developer browses API in development
- **WHEN** a developer visits the API root path with `DEBUG=True`
- **THEN** the system returns the DRF browsable API interface

### Requirement: Browsable API is disabled in production
The system MUST NOT expose the browsable API or API root listing when the application runs in production mode.

#### Scenario: Production hides the browser interface
- **WHEN** a request is made to the API browser path with `DEBUG=False`
- **THEN** the system returns a 404 response

### Requirement: Endpoint listing reflects registered routes
The system MUST display only the DRF-registered endpoints in the API browser listing.

#### Scenario: New endpoint appears in listing
- **WHEN** a new DRF viewset or API view is registered in the URL configuration
- **THEN** the API browser listing includes the new endpoint
