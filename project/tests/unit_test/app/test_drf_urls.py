import importlib
import os

import pytest
from django.conf import settings
from django.test import override_settings
from django.urls import resolve

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


@override_settings(ENVIRONMENT='production')
def test_api_routes_not_resolved_in_production():
    # urls.py reads settings.ENVIRONMENT at import time, so reload it in production mode.
    importlib.reload(urls)
    try:
        # The only production URL should be the admin.
        assert len(urls.urlpatterns) == 1
        assert any('admin/' in str(p.pattern) for p in urls.urlpatterns)
    finally:
        # Restore the development URL configuration for subsequent tests.
        importlib.reload(urls)
