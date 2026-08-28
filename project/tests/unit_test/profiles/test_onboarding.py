from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import pytest
from django.contrib.auth.models import Group
from django.urls import Resolver404, reverse

from profiles.admin.public_profile import PublicProfileAdmin, PublicProfileForm
from django.contrib.auth import get_user_model

from profiles.middleware import PublicProfileOnboardingMiddleware
from profiles.models import PublicProfile


User = get_user_model()


def _user(pk=1, username="test-user"):
    """Return a real unsaved User instance for assignment to PublicProfile."""
    return User(pk=pk, username=username, first_name="Test", last_name="User")


def _request_user(
    *,
    is_authenticated=True,
    is_staff=True,
    has_profile=False,
):
    """Return a lightweight fake user for middleware/admin permission tests."""
    user = SimpleNamespace(
        id=1,
        pk=1,
        username="test-user",
        first_name="Test",
        last_name="User",
        is_authenticated=is_authenticated,
        is_staff=is_staff,
        groups=MagicMock(),
    )
    if has_profile:
        user.public_profile = SimpleNamespace()
    return user


def _request(
    path="/admin/",
    *,
    is_authenticated=True,
    is_staff=True,
    has_profile=False,
):
    return SimpleNamespace(
        path=path,
        user=_request_user(
            is_authenticated=is_authenticated,
            is_staff=is_staff,
            has_profile=has_profile,
        ),
    )


class TestPublicProfileOnboardingMiddleware:
    @pytest.fixture
    def middleware(self):
        return PublicProfileOnboardingMiddleware(get_response=lambda request: "ok")

    def test_call_redirects_when_onboarding_required(self, middleware):
        request = _request(is_authenticated=True, is_staff=True)
        response = middleware(request)

        assert response.status_code == 302
        assert response["Location"] == reverse("admin:profiles_publicprofile_add")

    def test_call_continues_when_onboarding_not_required(self, middleware):
        request = _request(path="/admin/login/", is_authenticated=False)

        assert middleware(request) == "ok"

    def test_must_onboard_false_for_non_admin_path(self, middleware):
        request = _request(path="/", is_authenticated=True, is_staff=True)

        assert middleware._must_onboard(request) is False

    def test_must_onboard_false_for_anonymous_user(self, middleware):
        request = _request(is_authenticated=False)

        assert middleware._must_onboard(request) is False

    def test_must_onboard_false_for_non_staff_user(self, middleware):
        request = _request(is_authenticated=True, is_staff=False)

        assert middleware._must_onboard(request) is False

    def test_must_onboard_false_for_exempt_url(self, middleware):
        request = _request(path="/admin/login/", is_authenticated=True, is_staff=True)

        assert middleware._must_onboard(request) is False

    def test_must_onboard_false_when_profile_exists(self, middleware):
        request = _request(is_authenticated=True, is_staff=True, has_profile=True)

        assert middleware._must_onboard(request) is False

    def test_must_onboard_true_when_profile_missing(self, middleware):
        request = _request(
            path="/admin/profiles/publicprofile/",
            is_authenticated=True,
            is_staff=True,
        )

        assert middleware._must_onboard(request) is True

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/admin/login/", True),
            ("/admin/logout/", True),
            ("/admin/password_change/", True),
            ("/admin/password_change/done/", True),
            ("/admin/profiles/publicprofile/add/", True),
            ("/admin/profiles/publicprofile/", False),
            ("/admin/auth/group/", False),
        ],
    )
    def test_is_exempt_for_admin_urls(self, middleware, path, expected):
        request = _request(path=path)

        assert middleware._is_exempt(request) is expected

    def test_is_exempt_false_for_unresolvable_url(self, middleware, mocker):
        request = _request(path="/admin/not-a-real-url/")
        resolve_mock = mocker.patch("profiles.middleware.resolve")
        resolve_mock.side_effect = Resolver404

        assert middleware._is_exempt(request) is False


class TestPublicProfileForm:
    def test_form_omits_user_field(self):
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

    def test_form_accepts_user_keyword_only(self):
        user = _user(pk=1)
        form = PublicProfileForm(user=user)

        assert form.user is user

    def test_form_prefills_from_user(self):
        user = _user(pk=1, username="jdoe")
        user.first_name = "John"
        user.last_name = "Doe"
        form = PublicProfileForm(user=user)

        assert form.fields["public_username"].initial == "jdoe"
        assert form.fields["first_name"].initial == "John"
        assert form.fields["last_name"].initial == "Doe"

    def test_form_does_not_prefill_when_editing(self):
        user = _user(pk=1, username="jdoe")
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


class TestPublicProfileAdmin:
    @pytest.fixture
    def admin(self):
        from django.contrib import admin

        return PublicProfileAdmin(PublicProfile, admin.site)

    def test_get_form_binds_user_to_form_class(self, admin):
        request = _request(is_authenticated=True, is_staff=True)
        form_class = admin.get_form(request)
        form = form_class()

        assert form.user is request.user

    def test_get_queryset_returns_empty_when_request_is_none(self, admin):
        assert list(admin.get_queryset(None)) == []

    def test_get_queryset_filters_by_request_user(self, admin, mocker):
        queryset = mocker.MagicMock()
        mocker.patch.object(
            admin.__class__.__bases__[0],
            "get_queryset",
            return_value=queryset,
        )
        request = _request(is_authenticated=True, is_staff=True)

        admin.get_queryset(request)

        queryset.filter.assert_called_once_with(user_id=request.user.id)

    def test_has_module_permission_only_for_staff(self, admin):
        assert admin.has_module_permission(_request(is_staff=True)) is True
        assert admin.has_module_permission(_request(is_staff=False)) is False
        assert admin.has_module_permission(_request(is_authenticated=False)) is False
        assert admin.has_module_permission(None) is False

    def test_has_add_permission_for_staff_without_profile(self, admin, mocker):
        mocker.patch.object(
            PublicProfile.objects, "filter", return_value=Mock(exists=Mock(return_value=False))
        )
        request = _request(is_authenticated=True, is_staff=True)

        assert admin.has_add_permission(request) is True

    def test_has_add_permission_denied_when_profile_exists(self, admin, mocker):
        mocker.patch.object(
            PublicProfile.objects, "filter", return_value=Mock(exists=Mock(return_value=True))
        )
        request = _request(is_authenticated=True, is_staff=True)

        assert admin.has_add_permission(request) is False

    def test_has_add_permission_denied_for_non_staff_or_anonymous(self, admin):
        assert admin.has_add_permission(_request(is_staff=False)) is False
        assert admin.has_add_permission(_request(is_authenticated=False)) is False
        assert admin.has_add_permission(None) is False

    def test_has_change_permission_allows_owner(self, admin):
        own_profile = PublicProfile(user_id=1)
        other_profile = PublicProfile(user_id=2)
        request = _request(is_authenticated=True, is_staff=True)

        assert admin.has_change_permission(request, own_profile) is True
        assert admin.has_change_permission(request, other_profile) is False

    def test_has_change_permission_without_object_uses_profile_existence(self, admin, mocker):
        mocker.patch.object(
            PublicProfile.objects, "filter", return_value=Mock(exists=Mock(return_value=True))
        )
        request = _request(is_authenticated=True, is_staff=True)

        assert admin.has_change_permission(request) is True

    def test_has_change_permission_denied_for_non_staff_or_anonymous(self, admin):
        assert admin.has_change_permission(_request(is_staff=False)) is False
        assert admin.has_change_permission(_request(is_authenticated=False)) is False
        assert admin.has_change_permission(None) is False

    def test_save_model_assigns_request_user_on_creation(self, admin, mocker):
        user = _user(pk=1)
        request = SimpleNamespace(user=user)
        profile = PublicProfile()
        form = Mock()
        mocker.patch("django.db.models.Model.save")

        admin.save_model(request, profile, form, change=False)

        assert profile.user is user


class TestOnboardingGroup:
    def test_onboarding_group_name_matches_settings(self):
        from django.conf import settings

        assert settings.PUBLIC_PROFILE_ONBOARDING_GROUP_NAME == "Public Profile Onboarding"

    def test_migration_file_exists(self):
        import importlib

        migration_module = importlib.import_module(
            "profiles.migrations.0004_onboarding_group"
        )

        assert hasattr(migration_module, "create_onboarding_group")
        assert hasattr(migration_module, "remove_onboarding_group")


class TestOwnershipAndGroups:
    @pytest.fixture
    def admin(self):
        from django.contrib import admin

        return PublicProfileAdmin(PublicProfile, admin.site)

    def test_public_profile_rejects_user_reassignment(self, mocker):
        original = _user(pk=1)
        other = _user(pk=2)
        profile = PublicProfile(pk=1, user=original)
        profile.user = other

        mocker.patch.object(
            PublicProfile.objects,
            "filter",
            return_value=Mock(
                values_list=Mock(return_value=Mock(first=Mock(return_value=1)))
            ),
        )
        mocker.patch("django.db.models.Model.save")

        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError, match="cannot change"):
            profile.save()

    def test_user_cannot_create_profile_for_another_user(self, admin, mocker):
        staff_user = _user(pk=1)
        other_user = _user(pk=2)
        request = SimpleNamespace(user=staff_user)
        profile = PublicProfile()
        form = Mock()
        mocker.patch("django.db.models.Model.save")

        admin.save_model(request, profile, form, change=False)

        assert profile.user is staff_user
        assert profile.user is not other_user
