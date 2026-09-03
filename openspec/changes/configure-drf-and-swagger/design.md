## Context

The project is a Django 6.1 application with the usual admin interface and apps (`posts`, `profiles`, `clients`). It currently has no REST API tooling. Settings are environment-driven: `DEBUG` and `PRODUCTION` are read from environment variables, and `ALLOWED_HOSTS` is configurable. The root URL configuration only mounts the Django admin. See `proposal.md` for the motivation behind adding API infrastructure.

## Goals / Non-Goals

**Goals:**
- Add Django REST Framework as a runtime dependency and register it in `INSTALLED_APPS`.
- Configure sensible DRF defaults for authentication, permissions, pagination, and renderers.
- Wire DRF's API root/browsable API under a consistent path that is reachable only in development.
- Add `drf-spectacular` as a development-only dependency for OpenAPI schema generation.
- Expose the OpenAPI schema endpoint only in development.
- Verify the configuration with `manage.py check` and a smoke test of the dev-only routes.

**Non-Goals:**
- Creating actual API endpoints, serializers, or viewsets for existing models.
- Changing the existing authentication model or user flows.
- Adding versioning, throttling, or advanced DRF features beyond the baseline defaults.
- Modifying production deployment orchestration.

## Decisions

### Use `djangorestframework` as the runtime dependency
- **Rationale**: It is the standard, well-maintained toolkit for building REST APIs in Django and integrates cleanly with the existing Django project structure.
- **Alternatives considered**: Tastypie (less commonly used with modern Django), writing a custom JSON layer (reinvents the wheel). Neither is justified for a baseline API foundation.

### Use `drf-spectacular` for OpenAPI schema generation
- **Rationale**: `drf-spectacular` is the current community standard for DRF OpenAPI generation and supports emitting the schema as JSON/YAML. We will expose only the schema endpoint so external HTTP clients (e.g., Postman, Insomnia) can import it and configure their own interface.
- **Alternatives considered**: `drf-yasg` is older and in maintenance mode; `django-rest-swagger` is deprecated. `drf-spectacular` is the safer long-term choice.

### Gate browsable API and OpenAPI schema URLs with `DEBUG`
- **Rationale**: The project already derives `DEBUG` from the environment. Using the same flag keeps the rule simple and explicit: `DEBUG=False` means no development tooling is mounted.
- **Alternatives considered**: A separate `ENABLE_API_DOCS` setting. Rejected because it adds another environment variable without clear benefit when `DEBUG` already captures the intent.

### Keep `drf-spectacular` as a dev-only dependency
- **Rationale**: Production deployments should not install or import OpenAPI generation code, reducing attack surface and dependency footprint.
- **Implementation note**: Import `drf_spectacular` views lazily inside the `if DEBUG:` block in `urls.py` so the production code path never references the package.

### Default DRF settings
- **Authentication**: `SessionAuthentication` keeps parity with the existing Django admin/session auth.
- **Permissions**: `IsAuthenticatedOrReadOnly` allows safe public read access while requiring authentication for writes, which aligns with typical blog use cases until per-endpoint permissions are defined.
- **Pagination**: `PageNumberPagination` with a moderate page size prevents accidental large result sets.
- **Renderers**: `JSONRenderer` plus `BrowsableAPIRenderer` in development; production will not expose the browsable renderer because the corresponding URLs are not mounted.

## Risks / Trade-offs

- [Risk] Adding DRF to `INSTALLED_APPS` introduces a new dependency with its own security release cadence. → **Mitigation**: Pin a minimum stable version in `pyproject.toml` and keep it updated.
- [Risk] `IsAuthenticatedOrReadOnly` may be too permissive or too restrictive for future endpoints. → **Mitigation**: This is a default only; future endpoint specs can override permission classes explicitly.
- [Risk] Lazy imports in `urls.py` can be surprising to new contributors. → **Mitigation**: Add a short comment explaining why `drf_spectacular` views are imported inside the `DEBUG` block.
- [Risk] `drf-spectacular` dev-dependency means CI tests that import the schema URL must run with dev dependencies. → **Mitigation**: Document that the dev group must be installed for running the full test suite.

## Migration Plan

1. Run `uv add djangorestframework` to add the runtime dependency.
2. Run `uv add --dev drf-spectacular` to add the development-only OpenAPI schema tooling.
3. Add `'rest_framework'` to `INSTALLED_APPS` in `project/app/settings.py`.
4. Add a `REST_FRAMEWORK` settings block with authentication, permission, pagination, and renderer defaults.
5. In `project/app/urls.py`, import `rest_framework.urls` and mount the API root under a development-only conditional (`if DEBUG:`).
6. Inside the same `DEBUG` block, lazily import and mount the `drf_spectacular` schema view.
7. Run `uv run python project/manage.py check` to validate the configuration.
8. Optionally, run a focused smoke test that requests the dev-only routes with `DEBUG=True` and confirms 404s with `DEBUG=False`.

## Open Questions

None at this time.
