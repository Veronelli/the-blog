import re
from functools import cached_property
from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Variable(models.Model):
    identifier = models.CharField(max_length=32, unique=True)
    label = models.CharField(max_length=16)
    description = models.CharField(max_length=64)
    regex = models.CharField(max_length=255)

    class Meta:
        ordering = ("identifier",)

    def __str__(self) -> str:
        return self.identifier

    @cached_property
    def _pattern(self) -> re.Pattern[str]:
        return re.compile(self.regex)

    def matches(self, value: str) -> bool:
        return self._pattern.fullmatch(value) is not None

    def clean(self) -> None:
        super().clean()
        try:
            re.compile(self.regex)
        except re.error as exc:
            raise ValidationError({"regex": f"Invalid regular expression: {exc}"})


class SocialNetworkConfig(models.Model):
    name = models.CharField(max_length=64, unique=True)
    template_url = models.CharField(max_length=255)
    icon_url = models.CharField(max_length=255)
    variables: "models.ManyToManyField[Variable, SocialNetworkConfig]" = models.ManyToManyField(
        Variable, related_name="configs"
    )
    archived = models.BooleanField(default=False)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class SocialNetworkInstance(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_network_instances",
    )
    config = models.ForeignKey(
        SocialNetworkConfig,
        on_delete=models.PROTECT,
        related_name="instances",
    )
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.config.name} ({self.author})"


class VariableInstance(models.Model):
    social_network_instance = models.ForeignKey(
        SocialNetworkInstance,
        on_delete=models.PROTECT,
        related_name="variable_instances",
    )
    variable = models.ForeignKey(
        Variable, on_delete=models.PROTECT, related_name="instances"
    )
    value = models.CharField(max_length=255)
    archived = models.BooleanField(default=False)

    class Meta:
        ordering = ("variable__identifier",)

    def __str__(self) -> str:
        return f"{self.variable.identifier}={self.value}"

    @property
    def owner(self) -> Any:
        return self.social_network_instance.author

    def clean(self) -> None:
        super().clean()
        self._ensure_not_archived()
        self._ensure_identity_preserved()
        self._ensure_value_matches_regex()

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk is not None:
            self._ensure_not_archived()
            self._ensure_identity_preserved()
        super().save(*args, **kwargs)

    def archive(self) -> None:
        self.archived = True
        self.save(update_fields=["archived"])

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        if self.archived:
            raise models.ProtectedError(
                "Archived variable instances cannot be deleted.", {self}
            )
        return super().delete(*args, **kwargs)

    def _ensure_not_archived(self) -> None:
        if not self.pk:
            return
        archived = (
            VariableInstance.objects.filter(pk=self.pk)
            .values_list("archived", flat=True)
            .first()
        )
        if archived:
            raise ValidationError(
                "Archived variable instances cannot be modified."
            )

    def _ensure_identity_preserved(self) -> None:
        if not self.pk:
            return
        current = VariableInstance.objects.values(
            "variable_id", "social_network_instance_id"
        ).get(pk=self.pk)
        if current["variable_id"] != self.variable.pk:
            raise ValidationError(
                {"variable": "The variable of an instance cannot change."}
            )
        if current["social_network_instance_id"] != getattr(
            self, "social_network_instance_id"
        ):
            raise ValidationError(
                {
                    "social_network_instance": (
                        "The parent social network instance cannot change."
                    )
                }
            )

    def _ensure_value_matches_regex(self) -> None:
        if not self.variable.matches(self.value):
            raise ValidationError(
                {"value": "Value does not match the variable regex."}
            )
