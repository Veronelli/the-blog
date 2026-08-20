import pytest
from django.contrib import admin

from profiles.admin import VariableAdmin
from profiles.models import Variable


@pytest.fixture
def variable_admin() -> VariableAdmin:
    return VariableAdmin(Variable, admin.site)
