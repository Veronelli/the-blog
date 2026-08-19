from django.core.exceptions import ValidationError
from django.db import models as django_models
from django.test import TestCase

from profiles.models import Variable, VariableInstance


class VariableInstanceModelTests(TestCase):
    def setUp(self) -> None:
        self.variable = Variable.objects.create(
            identifier="username",
            label="Username",
            description="Social network username",
            regex=r"[A-Za-z0-9_]+",
        )
        self.user = self._build_user()
        self.social_network_instance = self._build_social_network_instance(self.user)

    def _build_user(self):
        from django.contrib.auth import get_user_model

        return get_user_model().objects.create_user(
            username="test-user",
            password="test-password",
        )

    def _build_social_network_instance(self, user):
        from profiles.models import SocialNetworkConfig, SocialNetworkInstance

        config = SocialNetworkConfig.objects.create(
            name="Example",
            template_url="https://example.test/{username}",
            icon_url="https://example.test/icon.svg",
        )
        config.variables.add(self.variable)
        return SocialNetworkInstance.objects.create(author=user, config=config)

    def test_save_valid_value_creates_instance(self) -> None:
        instance = VariableInstance(
            social_network_instance=self.social_network_instance,
            variable=self.variable,
            value="test_user",
        )

        instance.full_clean()
        instance.save()

        self.assertFalse(instance.archived)
        self.assertEqual(instance.value, "test_user")
        self.assertEqual(instance.variable, self.variable)
        self.assertEqual(
            instance.social_network_instance, self.social_network_instance
        )

    def test_save_invalid_value_is_rejected(self) -> None:
        instance = VariableInstance(
            social_network_instance=self.social_network_instance,
            variable=self.variable,
            value="test user",
        )

        with self.assertRaises(ValidationError):
            instance.full_clean()

    def test_owner_derives_from_parent_social_network_instance(self) -> None:
        instance = VariableInstance(
            social_network_instance=self.social_network_instance,
            variable=self.variable,
            value="test_user",
        )

        self.assertEqual(instance.owner, self.user)

    def test_update_value_while_active_keeps_variable_and_parent(self) -> None:
        instance = VariableInstance.objects.create(
            social_network_instance=self.social_network_instance,
            variable=self.variable,
            value="test_user",
        )

        instance.value = "another_user"
        instance.full_clean()
        instance.save()

        instance.refresh_from_db()
        self.assertEqual(instance.value, "another_user")
        self.assertEqual(instance.variable, self.variable)
        self.assertEqual(
            instance.social_network_instance, self.social_network_instance
        )
        self.assertFalse(instance.archived)

    def test_archive_marks_instance_as_archived_without_deleting(self) -> None:
        instance = VariableInstance.objects.create(
            social_network_instance=self.social_network_instance,
            variable=self.variable,
            value="test_user",
        )
        pk = instance.pk

        instance.archive()
        instance.refresh_from_db()

        self.assertTrue(instance.archived)
        self.assertTrue(VariableInstance.objects.filter(pk=pk).exists())

    def test_cannot_update_value_after_archive(self) -> None:
        instance = VariableInstance.objects.create(
            social_network_instance=self.social_network_instance,
            variable=self.variable,
            value="test_user",
        )
        instance.archive()

        instance.value = "another_user"
        with self.assertRaises(ValidationError):
            instance.full_clean()

    def test_archived_instance_cannot_be_physically_deleted(self) -> None:
        instance = VariableInstance.objects.create(
            social_network_instance=self.social_network_instance,
            variable=self.variable,
            value="test_user",
        )
        instance.archive()
        pk = instance.pk

        with self.assertRaises(django_models.ProtectedError):
            instance.delete()

        self.assertTrue(VariableInstance.objects.filter(pk=pk).exists())
