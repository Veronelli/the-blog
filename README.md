# My Blog

A personal blog and experimentation platform. The goal is to try out different
features — from LLM integrations and payment methods to click trackers and
social media — and publish posts about what is discovered and worth sharing.

## Tech Stack

- **Python** 3.14
- **Django** 6.1
- **Dependency management** via `uv`
- **Database** SQLite (development default)

## Project Structure

- `the_blog/` — Django project package (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`).
- New capabilities are added as isolated Django apps so experiments stay modular.

## Running Locally

```bash
uv sync
cd the_blog
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/`. The Django admin is available at
`http://127.0.0.1:8000/admin/`.
