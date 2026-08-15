import os
from importlib import reload

import django
import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from app.log_tracking import (
    BaseLogService,
    LogLevel,
    LogService,
    LogServiceRegistry,
    get_configured_service,
)
import app.settings as app_settings


class FakeLokiService(BaseLogService):
    service = LogService.GRAFANA_LOKI

    def emit(self, level, message, labels, metadata=None):
        return None


class FakeCloudWatchService(BaseLogService):
    service = LogService.CLOUDWATCH

    def emit(self, level, message, labels, metadata=None):
        return None


@pytest.fixture(autouse=True)
def reset_singletons():
    LogServiceRegistry.reset()
    yield
    LogServiceRegistry.reset()


def test_configured_service_is_validated_and_reused():
    class_path = f"{__name__}.FakeLokiService"

    with override_settings(LOG_TRACKING_SERVICE_CLASS=class_path):
        assert get_configured_service() is get_configured_service()


def test_invalid_configured_service_is_rejected():
    with override_settings(LOG_TRACKING_SERVICE_CLASS="app.log_tracking.registry.LogServiceRegistry"):
        with pytest.raises(ImproperlyConfigured, match="BaseLogService"):
            get_configured_service()


def test_registry_keeps_one_distinct_service_per_log_service():
    registry = LogServiceRegistry()

    loki = registry.get_or_create(LogService.GRAFANA_LOKI, FakeLokiService)
    cloudwatch = registry.get_or_create(LogService.CLOUDWATCH, FakeCloudWatchService)

    assert registry.get_or_create(LogService.GRAFANA_LOKI, FakeLokiService) is loki
    assert registry.get_or_create(LogService.CLOUDWATCH, FakeCloudWatchService) is cloudwatch
    assert loki is not cloudwatch


def test_registry_reset_discards_registered_services():
    registry = LogServiceRegistry()
    registry.get_or_create(LogService.GRAFANA_LOKI, FakeLokiService)

    LogServiceRegistry.reset()

    assert LogServiceRegistry() is not registry


def test_log_levels_are_limited_to_the_enum():
    assert LogLevel.INFO == "info"


def test_loki_configuration_uses_environment_variables(mocker):
    mocker.patch.dict(
        os.environ,
        {
            "LOG_TRACKING_LOKI_BASE_URL": "https://logs.example.test",
            "LOG_TRACKING_LOKI_TOKEN": "test-token",
        },
        clear=False,
    )

    reload(app_settings)

    assert app_settings.LOG_TRACKING_LOKI_BASE_URL == "https://logs.example.test"
    assert app_settings.LOG_TRACKING_LOKI_TOKEN == "test-token"
