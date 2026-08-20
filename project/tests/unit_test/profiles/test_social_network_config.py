from profiles.models import SocialNetworkConfig


def _config(**overrides) -> SocialNetworkConfig:
    defaults = {
        "name": "Example",
        "template_url": "https://example.test/{username}",
        "icon_url": "https://example.test/icon.svg",
    }
    defaults.update(overrides)
    return SocialNetworkConfig(**defaults)


def test_str_returns_name() -> None:
    config = _config(name="GitHub")

    assert str(config) == "GitHub"
