import pytest
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError

from clients.models import Client
from clients.validators import validate_domains
from tests.unit_test.functions._client import _client


# Model metadata tests


def test_client_str_returns_name() -> None:
    client = _client(name="ACME")

    assert str(client) == "ACME"


def test_client_name_field_is_unique() -> None:
    field = Client._meta.get_field("name")

    assert field.unique is True


def test_client_secret_field_is_unique_and_blank() -> None:
    field = Client._meta.get_field("secret")

    assert field.unique is True
    assert field.blank is True


# Creation and secret generation tests


@pytest.mark.django_db
def test_client_generates_secret_on_save() -> None:
    client = _client(name="auto-secret")

    assert not client.secret

    client.save()

    assert client.secret
    assert len(client.secret) > 0


@pytest.mark.django_db
def test_client_preserves_provided_secret() -> None:
    client = _client(name="provided-secret", secret="my-custom-secret")

    client.save()

    assert client.secret == "my-custom-secret"


@pytest.mark.django_db
def test_client_name_uniqueness_is_enforced() -> None:
    _client(name="duplicate").save()
    second = _client(name="duplicate")

    with pytest.raises(Exception):
        second.save()


# Domain validation tests


def test_validate_domains_accepts_valid_single_url() -> None:
    assert validate_domains("https://example.com") is None


def test_validate_domains_accepts_valid_multiple_urls() -> None:
    assert validate_domains("https://example.com,http://app.example.org") is None


def test_validate_domains_rejects_missing_protocol() -> None:
    with pytest.raises(ValidationError):
        validate_domains("example.com")


def test_validate_domains_rejects_empty_entry() -> None:
    with pytest.raises(ValidationError):
        validate_domains("https://example.com,")


def test_validate_domains_rejects_empty_value() -> None:
    with pytest.raises(ValidationError):
        validate_domains("")


# is_domain_allowed tests


def test_is_domain_allowed_returns_true_for_allowed_host() -> None:
    client = _client(domain="https://example.com,http://app.example.org")

    assert client.is_domain_allowed("example.com") is True
    assert client.is_domain_allowed("app.example.org") is True


def test_is_domain_allowed_returns_false_for_unknown_host() -> None:
    client = _client(domain="https://example.com")

    assert client.is_domain_allowed("evil.com") is False


# Permission helper tests


@pytest.mark.django_db
def test_has_perm_returns_true_for_direct_permission() -> None:
    client = _client(name="direct-perm")
    client.save()
    permission = Permission.objects.first()
    assert permission is not None
    client.permissions.add(permission)

    assert client.has_perm(permission.codename) is True


@pytest.mark.django_db
def test_has_perm_returns_true_for_group_permission() -> None:
    from django.contrib.auth.models import Group

    client = _client(name="group-perm")
    client.save()
    permission = Permission.objects.first()
    assert permission is not None
    group = Group.objects.create(name="test-group")
    group.permissions.add(permission)
    client.groups.add(group)

    assert client.has_perm(permission.codename) is True


@pytest.mark.django_db
def test_has_perm_returns_false_for_missing_permission() -> None:
    client = _client(name="no-perm")
    client.save()

    assert client.has_perm("nonexistent.permission") is False


@pytest.mark.django_db
def test_has_module_perms_returns_true_for_direct_app_permission() -> None:
    client = _client(name="module-perm")
    client.save()
    permission = Permission.objects.filter(content_type__app_label="auth").first()
    assert permission is not None
    client.permissions.add(permission)

    assert client.has_module_perms("auth") is True


@pytest.mark.django_db
def test_has_module_perms_returns_false_for_missing_app() -> None:
    client = _client(name="no-module-perm")
    client.save()

    assert client.has_module_perms("nonexistent") is False
