# Repository Guide

## Project

- This is a Django 6.1 project requiring Python >= 3.14; dependencies are managed with `uv` and the lockfile is `uv.lock`.
- Run commands from the repository root. `project/manage.py` sets `DJANGO_SETTINGS_MODULE=app.settings`; the configuration package is `project/app`, but its import name is `app`.
- Main Django apps live in `project/posts`, `project/profiles`, and `project/clients`; project wiring is in `project/app/settings.py` and `project/app/urls.py`.
- The default database is SQLite at `project/db.sqlite3` and is derived from `project/app/settings.py`; it is local state, not a source file.
- DRF routes, browsable API, and the development OpenAPI schema are currently registered only when `ENVIRONMENT=development`.

## Commands

- Install or refresh dependencies with `uv sync`; prefer `uv run` instead of manually activating a virtualenv.
- Run Django commands only as `uv run python project/manage.py <command>`; do not invoke `django-admin` from the repository root.
- Start development with `uv run python project/manage.py migrate` followed by `uv run python project/manage.py runserver`.
- Run all tests with `uv run pytest`; run one file with `uv run pytest project/tests/unit_test/<path>/test_<name>.py` or select tests with `uv run pytest -k <expression>`.
- Before handing off a Django change, run `uv run python project/manage.py check` and the relevant pytest tests; run the full suite for cross-app changes.
- For model changes, run `uv run python project/manage.py makemigrations` and then `uv run python project/manage.py migrate`.

## Testing

- Use function-based pytest tests in `project/tests/unit_test/`; pytest is configured with `DJANGO_SETTINGS_MODULE=app.settings` and `pythonpath = ["project"]`.
- Keep tests database-free by default. Mock ORM managers and `Model.save`; use `@pytest.mark.django_db` only when persistence is strictly required.
- Shared builders belong in `project/tests/unit_test/functions/_<module>.py`; app-specific mocks belong in `project/tests/unit_test/mocks/<app>/`.
- Every OpenSpec implementation subgroup must create its unit tests before or alongside its implementation. Do not defer test creation to a final testing phase.

## OpenSpec And Branches

- Treat each feature as an OpenSpec change. Before implementation, create proposal, design, specs, and `tasks.md`; include real **Non-Goals** in `design.md`.
- Keep OpenSpec tasks grouped by independently implementable subgroups, and include unit-test work in each subgroup from the start.
- For the repository workflow, proposal work uses `origin/<change_name>` and each implementation subgroup uses `feature/<change_name>/<subgroup>`; do not create or rename branches without explicit user approval.
- Do not implement application code during proposal/update planning workflows; use `/opsx-apply` only after the artifacts are approved.
- When archiving, sync delta specs into `openspec/specs/<capability>/spec.md` before moving the change to `openspec/changes/archive/`.

## Git

- Never commit, push, rebase, or otherwise mutate git without explicit approval for that specific action.
- Before any approved commit, inspect status and diff, stage only the logical change, and use the repository's `git-commit` skill with a Conventional Commit message. Never commit secrets or bypass hooks.
