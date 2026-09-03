# Repository Guide

## Django

- Use `uv`; install/sync dependencies with `uv sync` and run every Django command from the repository root as `uv run python project/manage.py <command>`.
- The Django settings package is `project/app`, but its import name is `app` (`DJANGO_SETTINGS_MODULE=app.settings`). Run commands through `project/manage.py`; do not invoke `django-admin` from the repository root.
- The local SQLite database is `project/db.sqlite3` (derived from `project/app/settings.py`) and is ignored. Apply model changes with `uv run python project/manage.py makemigrations` followed by `uv run python project/manage.py migrate`.
- Run focused verification with `uv run pytest`. Always run `uv run python project/manage.py check` before handing off a Django change.

## Testing

- Write tests with **pytest vanilla**. Avoid `@pytest.mark.django_db` unless persistence is strictly required.
- Mock Django ORM calls and `django.db.models.Model.save` to keep tests database-free. Shared test builders live under `project/tests/unit_test/functions/_<module>.py`; model-specific mocks under `project/tests/unit_test/mocks/<app>/`.

## Git And Commits

- **Never commit, push, rebase, or perform any git mutation without explicit user approval for that specific action.** A confirmation given earlier in the conversation does not authorize a later mutation; ask again each time.
- Use the local `git-commit` skill for every commit. It requires inspecting the diff/status, staging only the logical change, and using a Conventional Commit message. Do not commit secrets or bypass hooks.

## Branches And PRs

- Features follow the OpenSpec workflow. Branch naming conventions in this repo are mixed; **confirm the exact naming scheme with the user** before creating branches.
- Common patterns seen:
  - Parent integration branch: `feature/<change-name>` or `origin/<change-name>`.
  - Child task branches: `feature/<change-name>/<task-name>` or `origin/<change-name>/<task-name>`.
- Child PRs target the parent branch, never `develop`. Merge child PRs into the parent, then open a single feature PR from the parent to `develop`.
- Do not assume branch names; use exactly what the user specifies.

## OpenSpec

- Treat each special feature as an OpenSpec change. Before implementation, create its complete proposal, design, specs, and `tasks.md` using the repository's OpenSpec skills.
- In `design.md`, list **Non-Goals** that are real scope decisions for the change. Do not include generic presentation layers such as Swagger UI, API documentation sites, or similar tooling unless they are explicitly part of the request.
- When archiving a completed change, sync its delta specs to `openspec/specs/<capability>/spec.md` before moving the change directory to `openspec/changes/archive/`.
