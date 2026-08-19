import re
from typing import Any

from django.db import models


class Variable(models.Model):
    identifier: str
    label: str
    description: str
    regex: str

    objects: models.Manager["Variable"]

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def __str__(self) -> str: ...
    def matches(self, value: str) -> bool: ...
    def clean(self) -> None: ...


class SocialNetworkConfig(models.Model):
    name: str
    template_url: str
    icon_url: str
    variables: models.ManyToManyField[Variable, "SocialNetworkConfig"]
    archived: bool

    objects: models.Manager["SocialNetworkConfig"]

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def __str__(self) -> str: ...


class SocialNetworkInstance(models.Model):
    author_id: int | None
    author: Any
    config_id: int | None
    config: Any
    archived: bool
    created_at: Any

    objects: models.Manager["SocialNetworkInstance"]

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def __str__(self) -> str: ...


class VariableInstance(models.Model):
    social_network_instance_id: int | None
    social_network_instance: Any
    variable_id: int | None
    variable: Any
    value: str
    archived: bool

    objects: models.Manager["VariableInstance"]

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def __str__(self) -> str: ...
    @property
    def owner(self) -> Any: ...
    def clean(self) -> None: ...
    def save(self, *args: Any, **kwargs: Any) -> None: ...
    def archive(self) -> None: ...
    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]: ...
