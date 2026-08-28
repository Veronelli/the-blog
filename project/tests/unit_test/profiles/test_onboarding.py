import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.urls import reverse

from profiles.middleware import PublicProfileOnboardingMiddleware
from profiles.models import PublicProfile


User = get_user_model()


@pytest.fixture
def client():
    return Client(HTTP_HOST="localhost")


@pytest.fixture
def onboarding_group():
    return Group.objects.get(name=settings.PUBLIC_PROFILE_ONBOARDING_GROUP_NAME)


@pytest.fixture
def staff_user(db):
    user = User.objects.create_user(
        "staff-user", password="test-password", is_staff=True
    )
    return user


@pytest.fixture
def profiled_staff_user(db):
    user = User.objects.create_user(
        "profiled-staff", password="test-password", is_staff=True
    )
    PublicProfile.objects.create(
        user=user,
        public_username="profiled-staff",
        first_name="Profiled",
        last_name="Staff",
        title="Title",
        subtitle="Subtitle",
        specialty="Specialty",
        short_description="Description",
    )
    return user


@pytest.fixture
def other_staff_user(db):
    user = User.objects.create_user(
        "other-staff", password="test-password", is_staff=True
    )
    return user


@pytest.mark.django_db
def test_anonymous_user_is_redirected_to_login(client):
    response = client.get("/admin/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_non_staff_user_is_redirected_to_login(client, staff_user):
    staff_user.is_staff = False
    staff_user.save()
    client.force_login(staff_user)

    response = client.get("/admin/")

    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


@pytest.mark.django_db
def test_profileless_staff_user_is_redirected_to_onboarding(
    client, staff_user, onboarding_group
):
    staff_user.groups.add(onboarding_group)
    client.force_login(staff_user)

    response = client.get("/admin/")

    assert response.status_code == 302
    assert response["Location"] == reverse("admin:profiles_publicprofile_add")


@pytest.mark.django_db
def test_profileless_staff_user_can_access_onboarding_form(
    client, staff_user, onboarding_group
):
    staff_user.groups.add(onboarding_group)
    client.force_login(staff_user)

    response = client.get(reverse("admin:profiles_publicprofile_add"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_profileless_staff_user_is_redirected_from_any_admin_route(
    client, staff_user, onboarding_group
):
    staff_user.groups.add(onboarding_group)
    client.force_login(staff_user)

    response = client.get(reverse("admin:auth_group_changelist"))

    assert response.status_code == 302
    assert response["Location"] == reverse("admin:profiles_publicprofile_add")


@pytest.mark.django_db
def test_profileless_staff_user_can_logout(client, staff_user, onboarding_group):
    staff_user.groups.add(onboarding_group)
    client.force_login(staff_user)

    response = client.post(reverse("admin:logout"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_superuser_without_profile_is_redirected_to_onboarding(client):
    superuser = User.objects.create_superuser(
        "super-no-profile", password="test-password"
    )
    client.force_login(superuser)

    response = client.get("/admin/")

    assert response.status_code == 302
    assert response["Location"] == reverse("admin:profiles_publicprofile_add")


@pytest.mark.django_db
def test_staff_with_profile_sees_only_profile_module_without_tool_groups(
    client, profiled_staff_user
):
    client.force_login(profiled_staff_user)

    response = client.get("/admin/")

    assert response.status_code == 200
    content = response.content.decode()
    assert "Profiles" in content
    assert "Variables" not in content
    assert "Social network configs" not in content


@pytest.mark.django_db
def test_tool_group_reveals_corresponding_admin_section(
    client, profiled_staff_user
):
    variable_content_type = ContentType.objects.get(
        app_label="profiles", model="variable"
    )
    permission = Permission.objects.get(
        codename="change_variable", content_type=variable_content_type
    )
    tool_group = Group.objects.create(name="Variables")
    tool_group.permissions.add(permission)
    profiled_staff_user.groups.add(tool_group)
    client.force_login(profiled_staff_user)

    response = client.get("/admin/")

    assert response.status_code == 200
    assert "Variables" in response.content.decode()


@pytest.mark.django_db
def test_onboarding_group_only_contains_add_publicprofile_permission(
    onboarding_group,
):
    permissions = list(onboarding_group.permissions.values_list("codename", flat=True))

    assert permissions == ["add_publicprofile"]


@pytest.mark.django_db
def test_onboarding_group_only_grants_access_to_public_profile_add(
    client, staff_user, onboarding_group
):
    staff_user.groups.add(onboarding_group)
    client.force_login(staff_user)

    add_response = client.get(reverse("admin:profiles_publicprofile_add"))
    assert add_response.status_code == 200

    group_response = client.get(reverse("admin:auth_group_changelist"))
    assert group_response.status_code == 302


@pytest.mark.django_db
def test_creating_profile_does_not_change_user_groups(
    client, staff_user, onboarding_group
):
    staff_user.groups.add(onboarding_group)
    client.force_login(staff_user)

    client.post(
        reverse("admin:profiles_publicprofile_add"),
        {
            "public_username": "new-user",
            "first_name": "New",
            "last_name": "User",
            "title": "Title",
            "subtitle": "Subtitle",
            "specialty": "Specialty",
            "short_description": "Description",
        },
    )

    staff_user.refresh_from_db()
    assert list(staff_user.groups.all()) == [onboarding_group]


@pytest.mark.django_db
def test_valid_onboarding_creates_profile_for_session_user(
    client, staff_user, onboarding_group
):
    staff_user.groups.add(onboarding_group)
    client.force_login(staff_user)

    response = client.post(
        reverse("admin:profiles_publicprofile_add"),
        {
            "public_username": "session-user",
            "first_name": "Session",
            "last_name": "User",
            "title": "Title",
            "subtitle": "Subtitle",
            "specialty": "Specialty",
            "short_description": "Description",
        },
    )

    assert response.status_code == 302
    profile = PublicProfile.objects.get(user=staff_user)
    assert profile.public_username == "session-user"


@pytest.mark.django_db
def test_invalid_onboarding_keeps_user_on_form(
    client, staff_user, onboarding_group
):
    staff_user.groups.add(onboarding_group)
    client.force_login(staff_user)

    response = client.post(
        reverse("admin:profiles_publicprofile_add"),
        {
            "public_username": "",
            "first_name": "",
            "last_name": "",
            "title": "",
            "subtitle": "",
            "specialty": "",
            "short_description": "",
        },
    )

    assert response.status_code == 200
    assert b"errornote" in response.content
    assert not PublicProfile.objects.filter(user=staff_user).exists()


@pytest.mark.django_db
def test_user_cannot_create_profile_for_another_user(
    client, staff_user, other_staff_user, onboarding_group
):
    staff_user.groups.add(onboarding_group)
    client.force_login(staff_user)

    client.post(
        reverse("admin:profiles_publicprofile_add"),
        {
            "public_username": "impersonation",
            "first_name": "Impersonation",
            "last_name": "Attempt",
            "title": "Title",
            "subtitle": "Subtitle",
            "specialty": "Specialty",
            "short_description": "Description",
        },
    )

    assert PublicProfile.objects.filter(user=staff_user).exists()
    assert not PublicProfile.objects.filter(user=other_staff_user).exists()


@pytest.mark.django_db
def test_user_cannot_edit_other_user_profile(
    client, staff_user, other_staff_user, onboarding_group
):
    PublicProfile.objects.create(
        user=staff_user,
        public_username="own-profile",
        first_name="Own",
        last_name="Profile",
        title="Title",
        subtitle="Subtitle",
        specialty="Specialty",
        short_description="Description",
    )
    other_profile = PublicProfile.objects.create(
        user=other_staff_user,
        public_username="other-profile",
        first_name="Other",
        last_name="Profile",
        title="Title",
        subtitle="Subtitle",
        specialty="Specialty",
        short_description="Description",
    )
    staff_user.groups.add(onboarding_group)
    client.force_login(staff_user)

    response = client.get(
        reverse("admin:profiles_publicprofile_change", args=[other_profile.pk])
    )

    assert response.status_code in (302, 403)


@pytest.mark.django_db
def test_form_prefills_from_session_account(
    client, staff_user, onboarding_group
):
    staff_user.first_name = "Prefilled"
    staff_user.last_name = "Name"
    staff_user.save()
    staff_user.groups.add(onboarding_group)
    client.force_login(staff_user)

    response = client.get(reverse("admin:profiles_publicprofile_add"))
    content = response.content.decode()

    assert 'value="staff-user"' in content
    assert 'value="Prefilled"' in content
    assert 'value="Name"' in content


class TestPublicProfileOnboardingMiddleware:
    @pytest.fixture
    def middleware(self):
        return PublicProfileOnboardingMiddleware(get_response=lambda request: "ok")

    def _request(self, path, *, is_authenticated=False, is_staff=False, has_profile=False):
        from types import SimpleNamespace

        user = SimpleNamespace(
            is_authenticated=is_authenticated,
            is_staff=is_staff,
        )
        if has_profile:
            user.public_profile = SimpleNamespace()
        return SimpleNamespace(path=path, user=user)

    def test_call_redirects_when_onboarding_required(self, middleware):
        request = self._request("/admin/", is_authenticated=True, is_staff=True)
        response = middleware(request)

        assert response.status_code == 302
        assert response["Location"] == reverse("admin:profiles_publicprofile_add")

    def test_call_continues_when_onboarding_not_required(self, middleware):
        request = self._request("/admin/login/", is_authenticated=False)

        assert middleware(request) == "ok"

    def test_must_onboard_false_for_non_admin_path(self, middleware):
        request = self._request("/", is_authenticated=True, is_staff=True)

        assert middleware._must_onboard(request) is False

    def test_must_onboard_false_for_anonymous_user(self, middleware):
        request = self._request("/admin/", is_authenticated=False)

        assert middleware._must_onboard(request) is False

    def test_must_onboard_false_for_non_staff_user(self, middleware):
        request = self._request("/admin/", is_authenticated=True, is_staff=False)

        assert middleware._must_onboard(request) is False

    def test_must_onboard_false_for_exempt_url(self, middleware):
        request = self._request(
            "/admin/login/", is_authenticated=True, is_staff=True
        )

        assert middleware._must_onboard(request) is False

    def test_must_onboard_false_when_profile_exists(self, middleware):
        request = self._request(
            "/admin/", is_authenticated=True, is_staff=True, has_profile=True
        )

        assert middleware._must_onboard(request) is False

    def test_must_onboard_true_when_profile_missing(self, middleware):
        request = self._request(
            "/admin/profiles/publicprofile/", is_authenticated=True, is_staff=True
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
        request = self._request(path)

        assert middleware._is_exempt(request) is expected

    def test_is_exempt_false_for_unresolvable_url(self, middleware, mocker):
        request = self._request("/admin/not-a-real-url/")
        resolve = mocker.patch("profiles.middleware.resolve")
        from django.urls import Resolver404
        resolve.side_effect = Resolver404

        assert middleware._is_exempt(request) is False
