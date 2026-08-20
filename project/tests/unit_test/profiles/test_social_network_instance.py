from django.contrib.auth import get_user_model

from profiles.models import (
    SocialNetworkConfig,
    SocialNetworkInstance,
)


def _build_config() -> SocialNetworkConfig:
    config = SocialNetworkConfig(
        name="Example",
        template_url="https://example.test/{username}",
        icon_url="https://example.test/icon.svg",
    )
    config.id = 1  # type: ignore[attr-defined]
    return config


def _build_user():
    user = get_user_model()(username="test-user")
    user.id = 1  # type: ignore[attr-defined]
    return user


def _build_parent() -> SocialNetworkInstance:
    parent = SocialNetworkInstance(
        author=_build_user(),
        config=_build_config(),
    )
    parent.id = 1  # type: ignore[attr-defined]
    return parent


def test_str_returns_config_name_and_author() -> None:
    parent = _build_parent()

    assert str(parent) == "Example (test-user)"
