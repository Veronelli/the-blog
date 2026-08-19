import os

import django
import pytest

from tests.factories import (
    create_public_profile,
    create_social_network_config,
    create_social_network_instance,
    create_user,
    create_variable,
    create_variable_instance,
)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()


@pytest.fixture
def user_factory():
    return create_user


@pytest.fixture
def variable_factory():
    return create_variable


@pytest.fixture
def social_network_config_factory():
    return create_social_network_config


@pytest.fixture
def social_network_instance_factory():
    return create_social_network_instance


@pytest.fixture
def variable_instance_factory():
    return create_variable_instance


@pytest.fixture
def public_profile_factory():
    return create_public_profile
