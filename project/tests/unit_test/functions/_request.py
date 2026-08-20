from unittest.mock import MagicMock


def _request(*, is_staff: bool, has_perm: bool) -> MagicMock:
    request = MagicMock(name="request")
    request.user.is_staff = is_staff
    request.user.is_active = True
    request.user.has_perm.return_value = has_perm
    return request
