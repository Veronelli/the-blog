from django.contrib.auth import get_user_model

from profiles.models import (
    SocialNetworkConfig,
    SocialNetworkInstance,
    VariableInstance,
)

from tests.unit_test.functions._variable import _variable


def _build_user():
    user = get_user_model()(username="test-user")
    user.id = 1  # type: ignore[attr-defined]
    return user


def _build_config(**overrides) -> SocialNetworkConfig:
    defaults = {
        "name": "Example",
        "template_url": "https://example.test/{username}",
        "icon_url": "https://example.test/icon.svg",
    }
    defaults.update(overrides)
    config = SocialNetworkConfig(**defaults)
    config.id = 1  # type: ignore[attr-defined]
    return config


def _build_parent(
    user=None,
    config: SocialNetworkConfig | None = None,
) -> SocialNetworkInstance:
    if user is None:
        user = _build_user()
    if config is None:
        config = _build_config()
    parent = SocialNetworkInstance(author=user, config=config)
    parent.id = 1  # type: ignore[attr-defined]
    return parent


def _build_variable_instance(
    *,
    value: str = "test_user",
    variable=None,
    parent: SocialNetworkInstance | None = None,
    pk: int | None = None,
) -> VariableInstance:
    if variable is None:
        variable = _variable()
        variable.id = 1  # type: ignore[attr-defined]
    if parent is None:
        parent = _build_parent()
    return VariableInstance(
        pk=pk,
        social_network_instance=parent,
        variable=variable,
        value=value,
    )
