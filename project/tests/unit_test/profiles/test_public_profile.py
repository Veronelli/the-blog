import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from profiles.forms import PublicProfileForm
from profiles.models import PublicProfile

from tests.factories import create_public_profile


@pytest.fixture
def user_model():
    return get_user_model()


def test_profile_stores_constructor_attributes() -> None:
    profile = create_public_profile(
        public_username="octocat",
        first_name="Octo",
        last_name="Cat",
        title="Engineer",
        subtitle="Building cool things",
        specialty="Backend",
        short_description="Hello world",
        photo_url="https://example.test/avatar.png",
    )

    assert profile.public_username == "octocat"
    assert profile.first_name == "Octo"
    assert profile.last_name == "Cat"
    assert profile.title == "Engineer"
    assert profile.subtitle == "Building cool things"
    assert profile.specialty == "Backend"
    assert profile.short_description == "Hello world"
    assert profile.photo_url == "https://example.test/avatar.png"


def test_profile_str_returns_public_username() -> None:
    profile = create_public_profile(public_username="octocat")

    assert str(profile) == "octocat"


def test_profile_photo_url_can_be_blank() -> None:
    profile = create_public_profile(photo_url="")

    assert profile.photo_url == ""


def test_profile_user_is_related_to_auth_user() -> None:
    from django.conf import settings

    assert any(
        field.name == "user"
        and field.related_model._meta.label_lower
        == settings.AUTH_USER_MODEL.lower()
        for field in PublicProfile._meta.get_fields()
    )


def test_profile_public_username_field_is_unique() -> None:
    field = PublicProfile._meta.get_field("public_username")

    assert field.unique is True


def test_profile_photo_url_field_allows_blank() -> None:
    field = PublicProfile._meta.get_field("photo_url")

    assert field.blank is True


def test_form_uses_public_username_as_identifier() -> None:
    field = PublicProfileForm.base_fields["public_username"]

    assert field.required is True


def test_form_accepts_valid_attributes() -> None:
    form = PublicProfileForm()
    form.cleaned_data = {
        "public_username": "octocat",
        "first_name": "Octo",
        "last_name": "Cat",
        "title": "Engineer",
        "subtitle": "Building cool things",
        "specialty": "Backend",
        "short_description": "Hello world",
        "photo_url": "https://example.test/avatar.png",
    }

    cleaned = form.clean()

    assert cleaned["public_username"] == "octocat"


def test_form_accepts_blank_photo_url() -> None:
    form = PublicProfileForm()
    form.cleaned_data = {
        "public_username": "octocat",
        "first_name": "Octo",
        "last_name": "Cat",
        "title": "Engineer",
        "subtitle": "Building cool things",
        "specialty": "Backend",
        "short_description": "Hello world",
        "photo_url": "",
    }

    form.clean()


def test_form_rejects_invalid_photo_url() -> None:
    form = PublicProfileForm()
    form.cleaned_data = {
        "public_username": "octocat",
        "first_name": "Octo",
        "last_name": "Cat",
        "title": "Engineer",
        "subtitle": "Building cool things",
        "specialty": "Backend",
        "short_description": "Hello world",
        "photo_url": "not-a-url",
    }

    with pytest.raises(ValidationError) as exc_info:
        form.clean()

    assert "photo_url" in exc_info.value.message_dict