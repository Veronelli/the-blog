from django.conf import settings


def test_rest_framework_is_installed():
    assert 'rest_framework' in settings.INSTALLED_APPS


def test_rest_framework_authentication_default():
    assert settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] == [
        'rest_framework.authentication.SessionAuthentication',
    ]


def test_rest_framework_permission_default():
    assert settings.REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] == [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ]


def test_rest_framework_pagination_default():
    assert settings.REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS'] == (
        'rest_framework.pagination.PageNumberPagination'
    )
    assert settings.REST_FRAMEWORK['PAGE_SIZE'] == 20


def test_rest_framework_renderer_defaults():
    assert settings.REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] == [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ]


def test_environment_defaults_to_development():
    assert settings.ENVIRONMENT == 'development'
