## Why

The project needs a robust REST API foundation to support future client integrations and public endpoints. Django REST Framework provides the standard toolkit for building APIs in Django, while an OpenAPI schema document makes the API discoverable and testable during development without exposing internal tooling in production.

## What Changes

- Add `djangorestframework` as a runtime dependency and install it in the Django project.
- Configure Django settings for DRF, including authentication classes, permission classes, pagination, and renderer defaults.
- Wire DRF into the project's URL configuration.
- Add `drf-spectacular` (or an equivalent OpenAPI generator) as a development-only dependency to generate the OpenAPI schema.
- Mount the DRF browsable API and the OpenAPI schema endpoint under a development-only route that is disabled when `DEBUG=False`.
- Ensure production builds do not expose the browsable API or the OpenAPI schema endpoint.

## Capabilities

### New Capabilities

- `drf-core`: Install and configure Django REST Framework as the project's API toolkit.
- `api-browser`: Expose DRF's browsable API and endpoint listing only in development environments.
- `swagger-docs`: Generate and serve the OpenAPI schema document (JSON/YAML) from DRF serializers and views only in development environments.

### Modified Capabilities

<!-- No existing capability requirements are changing; this change adds foundational API infrastructure. -->

## Impact

- `pyproject.toml` / `uv` dependency declarations: adds runtime and dev dependencies.
- `project/app/settings.py`: adds DRF settings and environment-gated schema endpoint URL.
- `project/app/urls.py`: adds DRF and OpenAPI schema URL patterns under a development-only conditional.
- Development workflow: developers can browse API endpoints and download the OpenAPI schema at the configured dev-only paths.
- Production security: documentation and browsable API endpoints are not mounted when `DEBUG=False`.
