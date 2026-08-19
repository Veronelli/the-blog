from django.core.exceptions import ValidationError
from django.test import TestCase

from profiles.models import Variable


class VariableModelTests(TestCase):
    def test_create_variable_with_valid_fields_succeeds(self) -> None:
        variable = Variable(
            identifier="username",
            label="Username",
            description="Social network username",
            regex=r"[A-Za-z0-9_]+",
        )

        variable.full_clean()

        self.assertEqual(variable.identifier, "username")
        self.assertEqual(variable.label, "Username")
        self.assertEqual(variable.description, "Social network username")
        self.assertEqual(variable.regex, r"[A-Za-z0-9_]+")

    def test_label_cannot_exceed_sixteen_characters(self) -> None:
        variable = Variable(
            identifier="username",
            label="x" * 17,
            description="Social network username",
            regex=r"[A-Za-z0-9_]+",
        )

        with self.assertRaises(ValidationError):
            variable.full_clean()

    def test_description_cannot_exceed_sixty_four_characters(self) -> None:
        variable = Variable(
            identifier="username",
            label="Username",
            description="x" * 65,
            regex=r"[A-Za-z0-9_]+",
        )

        with self.assertRaises(ValidationError):
            variable.full_clean()

    def test_identifier_must_be_unique(self) -> None:
        Variable.objects.create(
            identifier="username",
            label="Username",
            description="Social network username",
            regex=r"[A-Za-z0-9_]+",
        )
        duplicate = Variable(
            identifier="username",
            label="Different",
            description="Another description",
            regex=r"[A-Za-z0-9_]+",
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_value_must_fully_match_variable_regex(self) -> None:
        variable = Variable(
            identifier="username",
            label="Username",
            description="Social network username",
            regex=r"[A-Za-z0-9_]+",
        )

        variable.full_clean()
        self.assertTrue(variable.matches("test_user"))
        self.assertFalse(variable.matches("test user"))
        self.assertFalse(variable.matches("test!"))
        self.assertFalse(variable.matches(""))
