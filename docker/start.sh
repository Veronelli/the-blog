#!/bin/sh

set -eu

uv sync --frozen
uv run python project/manage.py migrate
uv run python project/manage.py collectstatic --noinput

exec "$@"
