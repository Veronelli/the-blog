from tests.unit_test.functions._social_network import _build_parent


def test_str_returns_config_name_and_author() -> None:
    parent = _build_parent()

    assert str(parent) == "Example (test-user)"
