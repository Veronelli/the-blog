## Purpose

Django REST Framework core capability provides the foundational API toolkit for building, serializing, and serving RESTful endpoints within the Django project.

## ADDED Requirements

### Requirement: DRF is installed and registered
The system MUST install `djangorestframework` and register it as an installed Django application.

#### Scenario: Project starts successfully
- **WHEN** the Django development server starts
- **THEN** no `ImproperlyConfigured` or missing-app error is raised for `rest_framework`

### Requirement: DRF default settings are configured
The system MUST configure DRF default behavior for authentication, permissions, pagination, and renderers through Django settings.

#### Scenario: Default API behavior is predictable
- **WHEN** a request is made to any DRF endpoint
- **THEN** the response uses the configured authentication, permission, pagination, and renderer classes

### Requirement: DRF URLs are wired into the project
The system MUST include DRF's URL patterns under a consistent route prefix in the project's root URL configuration.

#### Scenario: API root is reachable
- **WHEN** a user visits the configured API root path
- **THEN** the system returns a DRF-generated listing of registered API endpoints
