import pytest
from django.contrib import admin

from profiles.admin import SocialNetworkConfigAdmin, VariableAdmin
from profiles.models import SocialNetworkConfig, Variable


@pytest.fixture
def variable_admin() -> VariableAdmin:
    return VariableAdmin(Variable, admin.site)


@pytest.fixture
def social_network_config_admin() -> SocialNetworkConfigAdmin:
    return SocialNetworkConfigAdmin(SocialNetworkConfig, admin.site)
