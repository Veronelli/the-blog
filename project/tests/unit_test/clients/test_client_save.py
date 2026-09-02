import pytest

from clients.models import Client
from tests.unit_test.functions._mock_manager import mock_relation_manager


@pytest.mark.django_db
def test_save_generates_secret_when_blank() -> None:
    client = Client(name="blank-secret", domain="https://example.com")
    assert not client.secret

    client.save()

    assert client.secret
    assert len(client.secret) > 0


@pytest.mark.django_db
def test_save_preserves_provided_secret() -> None:
    client = Client(
        name="provided-secret",
        domain="https://example.com",
        secret="my-custom-secret",
    )

    client.save()

    assert client.secret == "my-custom-secret"


@pytest.mark.django_db
def test_save_generates_unique_secrets_for_multiple_clients() -> None:
    first = Client(name="first", domain="https://first.com")
    second = Client(name="second", domain="https://second.com")

    first.save()
    second.save()

    assert first.secret != second.secret
