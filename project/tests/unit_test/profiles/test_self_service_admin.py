from types import SimpleNamespace

import pytest
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models as django_models

from profiles.models import PublicProfile
from profiles.admin.public_profile import PublicProfileAdmin, PublicProfileForm


User = get_user_model()


def _request(
    user_id: int = 1,
    *,
    is_active: bool = True,
    is_authenticated: bool = True,
    is_staff: bool = True,
    username: str = "test-user",
):
    return SimpleNamespace(
        user=SimpleNamespace(
            id=user_id,
            username=username,
            is_active=is_active,
            is_authenticated=is_authenticated,
            is_staff=is_staff,
        )
    )


@pytest.fixture
def public_profile_admin() -> PublicProfileAdmin:
    return PublicProfileAdmin(PublicProfile, admin.site)


def test_public_profile_form_omits_user_field() -> None:
    assert tuple(PublicProfileForm.base_fields) == (
        "public_username",
        "first_name",
        "last_name",
        "title",
        "subtitle",
        "specialty",
        "short_description",
        "photo_url",
    )


def test_public_profile_form_accepts_user_keyword_only() -> None:
    user = User(pk=1, username="owner")
    form = PublicProfileForm(user=user)

    assert form.user is user


def test_public_profile_form_prefills_from_user() -> None:
    user = User(
        pk=1,
        username="jdoe",
        first_name="John",
        last_name="Doe",
    )
    form = PublicProfileForm(user=user)

    assert form.fields["public_username"].initial == "jdoe"
    assert form.fields["first_name"].initial == "John"
    assert form.fields["last_name"].initial == "Doe"


def test_public_profile_form_does_not_prefill_when_editing() -> None:
    user = User(pk=1, username="jdoe", first_name="John", last_name="Doe")
    profile = PublicProfile(
        pk=1,
        user=user,
        public_username="existing",
        first_name="Existing",
        last_name="Profile",
        title="Title",
        subtitle="Subtitle",
        specialty="Specialty",
        short_description="Description",
    )
    form = PublicProfileForm(instance=profile, user=user)

    assert form.initial.get("public_username") == "existing"


@pytest.mark.django_db
def test_public_profile_admin_exposes_module_only_to_staff() -> None:
    profile_admin = PublicProfileAdmin(PublicProfile, admin.site)

    assert profile_admin.has_module_permission(_request(is_staff=True)) is True
    assert profile_admin.has_module_permission(_request(is_staff=False)) is False
    assert profile_admin.has_module_permission(_request(is_authenticated=False)) is False


@pytest.mark.django_db
def test_public_profile_admin_allows_add_when_profile_is_missing(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    user = User.objects.create_user(
        "add-when-missing", password="pw", is_staff=True
    )

    assert public_profile_admin.has_add_permission(_request(user.id)) is True


@pytest.mark.django_db
def test_public_profile_admin_denies_second_add(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    user = User.objects.create_user("second-add", password="pw", is_staff=True)
    PublicProfile.objects.create(
        user=user,
        public_username="second-add",
        first_name="Second",
        last_name="Add",
        title="Title",
        subtitle="Subtitle",
        specialty="Specialty",
        short_description="Description",
    )

    assert public_profile_admin.has_add_permission(_request(user.id)) is False


@pytest.mark.django_db
def test_public_profile_admin_denies_add_for_non_staff(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    user = User.objects.create_user("non-staff", password="pw", is_staff=False)

    assert public_profile_admin.has_add_permission(_request(user.id, is_staff=False)) is False


@pytest.mark.django_db
def test_public_profile_admin_allows_only_owner_to_change(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    own_profile = PublicProfile(user_id=1)
    other_profile = PublicProfile(user_id=2)
    request = _request()

    assert public_profile_admin.has_change_permission(request, own_profile) is True
    assert public_profile_admin.has_change_permission(request, other_profile) is False
    assert public_profile_admin.has_view_permission(request, own_profile) is True
    assert public_profile_admin.has_view_permission(request, other_profile) is False
    assert public_profile_admin.has_delete_permission(request, own_profile) is False


@pytest.mark.django_db
def test_public_profile_admin_allows_change_without_object_when_profile_exists(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    user = User.objects.create_user("change-existing", password="pw", is_staff=True)
    PublicProfile.objects.create(
        user=user,
        public_username="change-existing",
        first_name="Change",
        last_name="Existing",
        title="Title",
        subtitle="Subtitle",
        specialty="Specialty",
        short_description="Description",
    )

    assert public_profile_admin.has_change_permission(_request(user.id)) is True


@pytest.mark.django_db
def test_public_profile_admin_denies_change_without_object_when_profile_missing(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    user = User.objects.create_user("change-missing", password="pw", is_staff=True)

    assert public_profile_admin.has_change_permission(_request(user.id)) is False


@pytest.mark.django_db
def test_public_profile_admin_returns_empty_queryset_when_request_is_none(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    assert list(public_profile_admin.get_queryset(None)) == []


def test_public_profile_admin_denies_change_for_unauthenticated_request(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    assert public_profile_admin.has_change_permission(_request(is_authenticated=False)) is False
    assert public_profile_admin.has_change_permission(_request(is_staff=False)) is False


@pytest.mark.django_db
def test_public_profile_admin_filters_queryset_to_request_user(
    mocker, public_profile_admin: PublicProfileAdmin,
) -> None:
    owner = User.objects.create_user("queryset-owner", password="pw", is_staff=True)
    other = User.objects.create_user("queryset-other", password="pw", is_staff=True)
    own_profile = PublicProfile.objects.create(
        user=owner,
        public_username="queryset-owner",
        first_name="Owner",
        last_name="User",
        title="Title",
        subtitle="Subtitle",
        specialty="Specialty",
        short_description="Description",
    )
    PublicProfile.objects.create(
        user=other,
        public_username="queryset-other",
        first_name="Other",
        last_name="User",
        title="Title",
        subtitle="Subtitle",
        specialty="Specialty",
        short_description="Description",
    )

    queryset = public_profile_admin.get_queryset(_request(owner.id))

    assert list(queryset) == [own_profile]


@pytest.mark.django_db
def test_public_profile_admin_assigns_request_user_when_creating(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    user = User.objects.create_user("profile-owner", password="pw", is_staff=True)
    request = SimpleNamespace(user=user)
    profile = PublicProfile()
    form = mocker.MagicMock(spec=forms.ModelForm)
    mocker.patch.object(django_models.Model, "save")

    public_profile_admin.save_model(request, profile, form, change=False)

    assert profile.user is request.user


@pytest.mark.django_db
def test_public_profile_rejects_user_reassignment() -> None:
    original = User.objects.create_user("original", password="pw", is_staff=True)
    other = User.objects.create_user("other", password="pw", is_staff=True)
    profile = PublicProfile.objects.create(
        user=original,
        public_username="original",
        first_name="Original",
        last_name="User",
        title="Title",
        subtitle="Subtitle",
        specialty="Specialty",
        short_description="Description",
    )
    profile.user = other

    with pytest.raises(ValidationError, match="cannot change"):
        profile.save()
