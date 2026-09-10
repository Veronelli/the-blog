import importlib

import pytest
from django.conf import settings
from django.test import override_settings
from django.urls import Resolver404, clear_url_caches, resolve

from app import urls


def test_api_root_resolves_in_development():
    assert settings.ENVIRONMENT == 'development'
    resolved = resolve('/api/')
    assert resolved.url_name == 'api-root'


def test_api_auth_urls_resolves_in_development():
    resolved = resolve('/api/auth/login/')
    assert resolved.url_name == 'login'


def test_openapi_schema_resolves_in_development():
    resolved = resolve('/api/schema/')
    assert resolved.url_name == 'schema'


@pytest.mark.parametrize(
    "path",
    [
        "/api/authors/test-user.json",
        "/api/authors/test-user/posts.json",
    ],
)
def test_api_routes_do_not_accept_format_suffixes(path: str):
    with pytest.raises(Resolver404):
        resolve(path)


@override_settings(ENVIRONMENT='production')
def test_public_api_route_resolves_in_production():
    # urls.py reads settings.ENVIRONMENT at import time, so reload it in production mode.
    importlib.reload(urls)
    clear_url_caches()
    try:
        resolved = resolve('/api/authors/test-user/')
        assert resolved.url_name == 'author-detail'
        resolved = resolve('/api/authors/test-user/posts/')
        assert resolved.url_name == 'author-post-list'
        resolved = resolve('/api/authors/test-user/posts/test-post/')
        assert resolved.url_name == 'author-post-detail'

        with pytest.raises(Resolver404):
            resolve('/api/auth/login/')
        with pytest.raises(Resolver404):
            resolve('/api/schema/')
    finally:
        # Restore the development URL configuration for subsequent tests.
        importlib.reload(urls)
        clear_url_caches()
