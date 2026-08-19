from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from profiles.models import Variable


class VariableAdminRegistrationTests(TestCase):
    def test_variable_is_registered_in_default_admin_site(self) -> None:
        self.assertIn(Variable, admin.site._registry)


class VariableAdminPermissionTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.staff = User.objects.create_user(
            username="staff",
            password="password",
            is_staff=True,
        )
        self._grant_variable_permissions(self.staff)
        self.regular = User.objects.create_user(
            username="regular",
            password="password",
            is_staff=False,
        )
        self.variable = Variable.objects.create(
            identifier="username",
            label="Username",
            description="Social network username",
            regex=r"[A-Za-z0-9_]+",
        )

    def _grant_variable_permissions(self, user) -> None:
        from django.contrib.auth.models import Permission

        codenames = [
            "add_variable",
            "change_variable",
            "delete_variable",
            "view_variable",
        ]
        perms = Permission.objects.filter(codename__in=codenames)
        user.user_permissions.set(perms)

    def _client_for(self, user) -> Client:
        client = Client()
        client.force_login(user)
        return client

    def test_staff_can_access_variable_change_list(self) -> None:
        response = self._client_for(self.staff).get(
            reverse("admin:profiles_variable_changelist")
        )
        self.assertEqual(response.status_code, 200)

    def test_non_staff_cannot_access_variable_change_list(self) -> None:
        response = self._client_for(self.regular).get(
            reverse("admin:profiles_variable_changelist")
        )
        self.assertIn(response.status_code, (302, 403))

    def test_staff_can_create_variable_via_admin(self) -> None:
        response = self._client_for(self.staff).post(
            reverse("admin:profiles_variable_add"),
            data={
                "identifier": "post_url",
                "label": "Post URL",
                "description": "Public post URL identifier",
                "regex": r"[A-Za-z0-9_-]+",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Variable.objects.filter(identifier="post_url").exists())

    def test_non_staff_cannot_create_variable_via_admin(self) -> None:
        response = self._client_for(self.regular).post(
            reverse("admin:profiles_variable_add"),
            data={
                "identifier": "post_url",
                "label": "Post URL",
                "description": "Public post URL identifier",
                "regex": r"[A-Za-z0-9_-]+",
            },
        )
        self.assertIn(response.status_code, (302, 403))
        self.assertFalse(Variable.objects.filter(identifier="post_url").exists())

    def test_staff_can_change_variable_via_admin(self) -> None:
        response = self._client_for(self.staff).post(
            reverse(
                "admin:profiles_variable_change", args=[self.variable.pk]
            ),
            data={
                "identifier": self.variable.identifier,
                "label": "Handle",
                "description": self.variable.description,
                "regex": self.variable.regex,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.variable.refresh_from_db()
        self.assertEqual(self.variable.label, "Handle")

    def test_non_staff_cannot_change_variable_via_admin(self) -> None:
        response = self._client_for(self.regular).post(
            reverse(
                "admin:profiles_variable_change", args=[self.variable.pk]
            ),
            data={
                "identifier": self.variable.identifier,
                "label": "Handle",
                "description": self.variable.description,
                "regex": self.variable.regex,
            },
        )
        self.assertIn(response.status_code, (302, 403))
        self.variable.refresh_from_db()
        self.assertEqual(self.variable.label, "Username")

    def test_staff_can_delete_variable_via_admin(self) -> None:
        response = self._client_for(self.staff).post(
            reverse(
                "admin:profiles_variable_delete", args=[self.variable.pk]
            ),
            data={"post": "yes"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Variable.objects.filter(pk=self.variable.pk).exists())

    def test_non_staff_cannot_delete_variable_via_admin(self) -> None:
        response = self._client_for(self.regular).post(
            reverse(
                "admin:profiles_variable_delete", args=[self.variable.pk]
            ),
            data={"post": "yes"},
        )
        self.assertIn(response.status_code, (302, 403))
        self.assertTrue(Variable.objects.filter(pk=self.variable.pk).exists())
