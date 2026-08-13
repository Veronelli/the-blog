# my_blog

Proyecto de blog construido con **Django 6.1** y gestionado con **uv**.

## Requisitos

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/)

## Instalación

```bash
# Crear el entorno virtual e instalar dependencias
uv sync
```

> **Nota:** se recomienda usar `uv run` en lugar de activar el entorno virtual manualmente: es mucho más rápido y no requiere activar nada.

## Puesta en marcha

```bash
# Aplicar migraciones
uv run python project/manage.py migrate

# Arrancar el servidor de desarrollo
uv run python project/manage.py runserver
```

El servidor estará disponible en <http://127.0.0.1:8000/>.

## Estructura del proyecto

```
my_blog/
├── project/              # Proyecto Django
│   ├── manage.py
│   └── app/              # Configuración del proyecto (paquete interno)
│       ├── settings.py
│       ├── urls.py
│       ├── asgi.py
│       └── wsgi.py
├── pyproject.toml         # Dependencias y metadatos (uv)
├── uv.lock
└── main.py                # Punto de entrada alternativo (demo)
```

## Configuración

Las opciones principales viven en `project/app/settings.py`:

| Clave           | Valor por defecto      | Descripción                                                        |
|-----------------|------------------------|--------------------------------------------------------------------|
| `SECRET_KEY`    | `django-insecure-...`  | Clave secreta. **Debe cambiarse en producción.**                   |
| `DEBUG`         | `True`                 | Modo debug. **Debe ser `False` en producción.**                    |
| `ALLOWED_HOSTS` | `[]`                   | Hosts permitidos. Añadir los dominios de despliegue en producción. |
| `DATABASES`     | SQLite (`db.sqlite3`)  | Base de datos por defecto.                                         |

## Scripts útiles

```bash
# Crear un superusuario para el admin
uv run python project/manage.py createsuperuser

# Ejecutar checks del proyecto
uv run python project/manage.py check
```

## Historial de renombrado

El paquete del proyecto Django cambió de nombre a lo largo del tiempo. Esto explica
por qué la estructura puede no coincidir con la que generaría `django-admin startproject`:

| Etapa            | Ubicación original            | Ubicación actual   |
|------------------|-------------------------------|--------------------|
| Inicial          | `the_blog/the_blog/`          | —                  |
| Renombrado #1    | `project/the_blog/`           | —                  |
| Renombrado #2    | `project/project/`            | —                  |
| Actual           | `project/app/`                | `project/app/`     |

El motivo del cambio fue simplificar y unificar los nombres de la estructura. Tras el
último renombrado, las referencias internas del módulo apuntan a `app.*`
(`DJANGO_SETTINGS_MODULE = 'app.settings'`, `ROOT_URLCONF = 'app.urls'`,
`WSGI_APPLICATION = 'app.wsgi.application'`).

> **Importante:** si se renombra de nuevo el paquete interno, hay que actualizar
> `DJANGO_SETTINGS_MODULE` en `manage.py`, `asgi.py` y `wsgi.py`, además de
> `ROOT_URLCONF` y `WSGI_APPLICATION` en `settings.py`.

## Estado actual

- Proyecto Django recién inicializado (solo configuración base).
- Admin de Django disponible en `/admin/`.
- Sin aplicaciones propias todavía.
