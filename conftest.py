import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()


pytest_plugins = [
    "tests.unit_test.fixture.factory_fixture",
    "tests.unit_test.fixture.admin_fixture",
]
