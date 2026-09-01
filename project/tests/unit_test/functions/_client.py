from typing import Any

from clients.models import Client


def _client(**overrides: Any) -> Client:
    defaults = {
        "name": "test-client",
        "domain": "https://example.com",
    }
    defaults.update(overrides)
    return Client(**defaults)
