from tests.unit_test.functions._social_network import _build_config


def test_str_returns_name() -> None:
    config = _build_config(name="GitHub")

    assert str(config) == "GitHub"
