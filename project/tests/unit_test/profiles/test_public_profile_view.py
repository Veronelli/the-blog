from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from django.http import Http404, HttpRequest

from profiles import views
from profiles.models import PublicProfile, SocialNetworkInstance


def _build_profile() -> MagicMock:
    profile = MagicMock(spec=PublicProfile)
    profile.user = MagicMock()
    profile.public_username = "alice-public"
    profile.first_name = "Alice"
    profile.last_name = "Smith"
    profile.title = "Engineer"
    profile.subtitle = "Hello world"
    profile.specialty = "Backend"
    profile.short_description = "About me."
    profile.photo_url = "https://example.test/alice.png"
    return profile


def _build_instance(*, url: str | None = "https://github.com/octocat") -> MagicMock:
    instance = MagicMock(spec=SocialNetworkInstance)
    instance.url = url
    return instance


@patch("profiles.views.render")
@patch("profiles.views.SocialNetworkInstance.objects.filter")
@patch("profiles.views.get_object_or_404")
def test_public_profile_view_renders_profile_and_active_instances(
    mock_get_object_or_404,
    mock_filter,
    mock_render,
) -> None:
    profile = _build_profile()
    mock_get_object_or_404.return_value = profile
    active_instance = _build_instance()
    archived_instance = _build_instance(url=None)
    mock_filter.return_value = [active_instance, archived_instance]
    request = HttpRequest()

    response = views.public_profile(request, profile.public_username)

    mock_get_object_or_404.assert_called_once_with(
        PublicProfile, public_username=profile.public_username
    )
    mock_filter.assert_called_once_with(author=profile.user, archived=False)
    mock_render.assert_called_once_with(
        request,
        "profiles/public_profile.html",
        {
            "profile": profile,
            "instances": [active_instance, archived_instance],
            "instance_urls": [
                {"instance": active_instance, "url": active_instance.url}
            ],
        },
    )
    assert response == mock_render.return_value


@patch("profiles.views.get_object_or_404")
def test_public_profile_view_propagates_404_for_unknown_username(
    mock_get_object_or_404,
) -> None:
    mock_get_object_or_404.side_effect = Http404()
    request = HttpRequest()

    with pytest.raises(Http404):
        views.public_profile(request, "ghost")


@patch("profiles.views.render")
@patch("profiles.views.SocialNetworkInstance.objects.filter")
@patch("profiles.views.get_object_or_404")
def test_public_profile_view_omits_instances_without_url(
    mock_get_object_or_404,
    mock_filter,
    mock_render,
) -> None:
    profile = _build_profile()
    mock_get_object_or_404.return_value = profile
    complete_instance = _build_instance()
    incomplete_instance = _build_instance(url=None)
    mock_filter.return_value = [complete_instance, incomplete_instance]
    request = HttpRequest()

    views.public_profile(request, profile.public_username)

    context = mock_render.call_args[0][2]
    assert context["instance_urls"] == [
        {"instance": complete_instance, "url": complete_instance.url}
    ]
