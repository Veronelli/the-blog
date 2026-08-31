import pytest
from django.core.exceptions import ValidationError

from profiles.models import PublicProfile

from tests.factories import create_public_profile


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


def test_profile_public_username_field_is_unique() -> None:
    field = PublicProfile._meta.get_field("public_username")

    assert field.unique is True


def test_profile_photo_url_field_allows_blank() -> None:
    field = PublicProfile._meta.get_field("photo_url")

    assert field.blank is True


def test_profile_public_username_is_required() -> None:
    profile = create_public_profile()
    profile.public_username = ""

    with pytest.raises(ValidationError) as exc_info:
        profile.full_clean(exclude={"user"})

    assert "public_username" in exc_info.value.message_dict


@pytest.mark.django_db
def test_profile_accepts_valid_photo_url() -> None:
    profile = create_public_profile(photo_url="https://example.test/avatar.png")

    profile.full_clean(exclude={"user"})

    assert profile.photo_url == "https://example.test/avatar.png"


@pytest.mark.django_db
def test_profile_accepts_blank_photo_url() -> None:
    profile = create_public_profile(photo_url="")

    profile.full_clean(exclude={"user"})


@pytest.mark.django_db
def test_profile_rejects_invalid_photo_url() -> None:
    profile = create_public_profile(photo_url="not-a-url")

    with pytest.raises(ValidationError) as exc_info:
        profile.full_clean(exclude={"user"})

    assert "photo_url" in exc_info.value.message_dict
