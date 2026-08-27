from types import SimpleNamespace

import pytest
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models as django_models

from profiles.models import PublicProfile
from profiles.self_service_admin import (
    PublicProfileAdmin,
    PublicProfileForm,
    SelfServiceAdminSite,
    self_service_admin_site,
)


def _request(user_id: int = 1, *, is_active: bool = True, is_authenticated: bool = True):
    return SimpleNamespace(
        user=SimpleNamespace(
            id=user_id, is_active=is_active, is_authenticated=is_authenticated
        )
    )


@pytest.fixture
def public_profile_admin() -> PublicProfileAdmin:
    return PublicProfileAdmin(PublicProfile, self_service_admin_site)


def test_self_service_site_registers_only_public_profile() -> None:
    assert set(self_service_admin_site._registry) == {PublicProfile}


def test_self_service_site_accepts_any_active_authenticated_user() -> None:
    site = SelfServiceAdminSite(name="test_self_service")

    assert site.has_permission(_request()) is True
    assert site.has_permission(_request(is_active=False)) is False
    assert site.has_permission(_request(is_authenticated=False)) is False


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


def test_public_profile_admin_makes_user_read_only(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    assert public_profile_admin.readonly_fields == ("user",)


def test_public_profile_admin_always_exposes_its_module(
    public_profile_admin: PublicProfileAdmin,
) -> None:
    assert public_profile_admin.has_module_permission(_request()) is True


def test_public_profile_admin_allows_add_when_profile_is_missing(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    mocker.patch.object(PublicProfile, "objects")
    PublicProfile.objects.filter.return_value.exists.return_value = False

    assert public_profile_admin.has_add_permission(_request()) is True


def test_public_profile_admin_denies_second_add(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    mocker.patch.object(PublicProfile, "objects")
    PublicProfile.objects.filter.return_value.exists.return_value = True

    assert public_profile_admin.has_add_permission(_request()) is False


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


def test_public_profile_admin_allows_change_without_object_when_profile_exists(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    mocker.patch.object(PublicProfile, "objects")
    PublicProfile.objects.filter.return_value.exists.return_value = True

    assert public_profile_admin.has_change_permission(_request()) is True


def test_public_profile_admin_denies_change_without_object_when_profile_missing(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    mocker.patch.object(PublicProfile, "objects")
    PublicProfile.objects.filter.return_value.exists.return_value = False

    assert public_profile_admin.has_change_permission(_request()) is False


def test_public_profile_admin_filters_queryset_to_request_user(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    queryset = mocker.MagicMock()
    mocker.patch.object(admin.ModelAdmin, "get_queryset", return_value=queryset)
    request = _request()

    assert public_profile_admin.get_queryset(request) is queryset.filter.return_value
    queryset.filter.assert_called_once_with(user=request.user)


def test_public_profile_admin_assigns_request_user_when_creating(
    mocker, public_profile_admin: PublicProfileAdmin
) -> None:
    user = get_user_model()(pk=1, username="profile-owner")
    request = SimpleNamespace(user=user)
    profile = PublicProfile()
    form = mocker.MagicMock(spec=forms.ModelForm)
    mocker.patch.object(django_models.Model, "save")

    public_profile_admin.save_model(request, profile, form, change=False)

    assert profile.user is request.user


def test_self_service_site_index_redirects_user_without_profile(mocker) -> None:
    site = SelfServiceAdminSite(name="test_self_service")
    request = _request()
    response = mocker.MagicMock()
    mocker.patch.object(PublicProfile, "objects")
    redirect_mock = mocker.patch(
        "profiles.self_service_admin.redirect", return_value=response
    )
    PublicProfile.objects.filter.return_value.exists.return_value = False

    assert site.index(request) is response
    redirect_mock.assert_called_once_with("test_self_service:profiles_publicprofile_add")


def test_self_service_site_index_renders_dashboard_with_profile(mocker) -> None:
    site = SelfServiceAdminSite(name="test_self_service")
    request = _request()
    response = mocker.MagicMock()
    mocker.patch.object(PublicProfile, "objects")
    mocker.patch.object(admin.AdminSite, "index", return_value=response)
    PublicProfile.objects.filter.return_value.exists.return_value = True

    assert site.index(request) is response
    admin.AdminSite.index.assert_called_once_with(request, None)


def test_public_profile_rejects_user_reassignment(mocker) -> None:
    mocker.patch.object(PublicProfile, "objects")
    PublicProfile.objects.filter.return_value.values_list.return_value.first.return_value = 1
    profile = PublicProfile(pk=1, user_id=2)

    with pytest.raises(ValidationError, match="cannot change"):
        profile.save()
