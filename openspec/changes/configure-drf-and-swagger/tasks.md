## 1. Dependencies

- [ ] 1.1 Add `djangorestframework` as a runtime dependency with `uv add djangorestframework`.
- [ ] 1.2 Add `drf-spectacular` as a development dependency with `uv add --dev drf-spectacular`.
- [ ] 1.3 Verify the lockfile is updated and both packages install cleanly with `uv sync`.

## 2. DRF Core Configuration

- [ ] 2.1 Register `'rest_framework'` in `INSTALLED_APPS` inside `project/app/settings.py`.
- [ ] 2.2 Add a `REST_FRAMEWORK` settings block with default authentication (`SessionAuthentication`), permissions (`IsAuthenticatedOrReadOnly`), pagination (`PageNumberPagination`), and renderers (`JSONRenderer` + `BrowsableAPIRenderer`).
- [ ] 2.3 Mount the DRF API root/browsable API URLs under a path prefix (e.g., `api/`) in `project/app/urls.py`, gated by `if DEBUG:`.

## 3. OpenAPI Schema Configuration

- [ ] 3.1 Add a `SPECTACULAR_SETTINGS` block in `project/app/settings.py` with project metadata and sane defaults.
- [ ] 3.2 Import `drf_spectacular` views lazily inside the `if DEBUG:` block in `project/app/urls.py`.
- [ ] 3.3 Mount the OpenAPI schema endpoint under a path prefix (e.g., `api/schema/`) inside the same `if DEBUG:` block.

## 4. Verification

- [ ] 4.1 Run `uv run python project/manage.py check` and confirm no errors or warnings.
- [ ] 4.2 Start the development server with `DEBUG=True` and verify the DRF browsable API root returns a 200 response.
- [ ] 4.3 With `DEBUG=True`, verify the OpenAPI schema endpoint returns valid JSON/YAML.
- [ ] 4.4 Run the application with `DEBUG=False` and confirm requests to the API browser and OpenAPI schema endpoint return 404 responses.
