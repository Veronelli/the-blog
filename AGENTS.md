# Repository Guide

## Django

- Use `uv`; install/sync dependencies with `uv sync` and run every Django command from the repository root as `uv run python project/manage.py <command>`.
- The Django settings package is `project/app`, but its import name is `app` (`DJANGO_SETTINGS_MODULE=app.settings`). Run commands through `project/manage.py`; do not invoke `django-admin` from the repository root.
- The local SQLite database is `project/db.sqlite3` (derived from `project/app/settings.py`) and is ignored. Apply model changes with `uv run python project/manage.py makemigrations` followed by `uv run python project/manage.py migrate`.
- Run focused verification with `uv run python project/manage.py test`; always run `uv run python project/manage.py check` before handing off a Django change.

## OpenSpec And Branches

- Treat each special feature as an OpenSpec change. Before implementation, create its complete proposal, design, specs, and `tasks.md` using the repository's OpenSpec skills.
- Start the feature parent branch from `develop` and name it `feature/<change-name>`. Commit the complete OpenSpec proposal on this branch; it is the integration branch for the feature.
- After `tasks.md` defines the segments, create one child branch per task from the feature parent: `feature/<change-name>/<task-name>`.
- Each task PR must target `feature/<change-name>`, never `develop`. Merge child PRs into the parent for small reviews, then open the single feature PR from `feature/<change-name>` to `develop`.
- Use the local `git-commit` skill for every commit. It requires inspecting the diff/status, staging only the logical change, and using a Conventional Commit message. Do not commit secrets or bypass hooks.
