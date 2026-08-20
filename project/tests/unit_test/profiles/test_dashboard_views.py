from __future__ import annotations

from typing import Any

import pytest
from django.test import Client
from django.urls import reverse

from profiles.models import PublicProfile, SocialNetworkInstance, VariableInstance

from tests.factories import (
    create_public_profile,
    create_social_network_config,
    create_user,
    create_variable,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> Any:
    user = create_user(username="alice", password="alice-password")
    user.set_password("alice-password")
    user.save()
    return user


@pytest.fixture
def other_user() -> Any:
    other = create_user(username="bob", password="bob-password")
    other.set_password("bob-password")
    other.save()
    return other


@pytest.fixture
def auth_client(user) -> Client:
    client = Client()
    client.login(username="alice", password="alice-password")
    return client


@pytest.fixture
def other_auth_client(other_user) -> Client:
    client = Client()
    client.login(username="bob", password="bob-password")
    return client


@pytest.fixture
def username_variable():
    variable = create_variable(identifier="username")
    variable.save()
    return variable


@pytest.fixture
def github_config(username_variable):
    config = create_social_network_config(
        name="GitHub",
        template_url="https://github.com/{username}",
        icon_url="https://example.test/github.svg",
    )
    config.save()
    config.variables.add(username_variable)
    return config


def test_dashboard_redirects_anonymous_user_to_login() -> None:
    client = Client()
    response = client.get(reverse("profiles:dashboard"))

    assert response.status_code == 302
    assert "login" in response.url


def test_dashboard_renders_for_authenticated_user(auth_client) -> None:
    response = auth_client.get(reverse("profiles:dashboard"))

    assert response.status_code == 200


def test_dashboard_creates_profile_when_missing(auth_client, user) -> None:
    assert not PublicProfile.objects.filter(user=user).exists()

    response = auth_client.post(
        reverse("profiles:dashboard"),
        data={
            "public_username": "alice-public",
            "first_name": "Alice",
            "last_name": "Smith",
            "title": "Engineer",
            "subtitle": "Hello",
            "specialty": "Backend",
            "short_description": "About me.",
            "photo_url": "https://example.test/alice.png",
        },
    )

    assert response.status_code == 302
    profile = PublicProfile.objects.get(user=user)
    assert profile.public_username == "alice-public"
    assert profile.first_name == "Alice"


def test_dashboard_updates_existing_profile(auth_client, user) -> None:
    create_public_profile(
        user=user,
        public_username="alice-old",
        first_name="Alice",
        last_name="Smith",
        title="Engineer",
        subtitle="Hello",
        specialty="Backend",
        short_description="About me.",
    ).save()

    response = auth_client.post(
        reverse("profiles:dashboard"),
        data={
            "public_username": "alice-new",
            "first_name": "Alice",
            "last_name": "Smith",
            "title": "Engineer",
            "subtitle": "Hello",
            "specialty": "Backend",
            "short_description": "About me.",
            "photo_url": "",
        },
    )

    assert response.status_code == 302
    profile = PublicProfile.objects.get(user=user)
    assert profile.public_username == "alice-new"


def test_dashboard_rejects_invalid_photo_url(auth_client) -> None:
    response = auth_client.post(
        reverse("profiles:dashboard"),
        data={
            "public_username": "alice",
            "first_name": "Alice",
            "last_name": "Smith",
            "title": "Engineer",
            "subtitle": "Hello",
            "specialty": "Backend",
            "short_description": "About me.",
            "photo_url": "not-a-url",
        },
    )

    assert response.status_code == 200
    assert not PublicProfile.objects.filter(public_username="alice").exists()


def test_dashboard_only_lists_current_user_instances(
    auth_client, user, other_user, github_config, username_variable
) -> None:
    own = SocialNetworkInstance.objects.create(author=user, config=github_config)
    other = SocialNetworkInstance.objects.create(author=other_user, config=github_config)

    response = auth_client.get(reverse("profiles:dashboard"))

    assert response.status_code == 200
    own_ids = [instance.pk for instance in response.context["instances"]]
    assert own.pk in own_ids
    assert other.pk not in own_ids


def test_dashboard_creates_social_network_instance(auth_client, github_config) -> None:
    response = auth_client.post(
        reverse("profiles:dashboard_instance_create"),
        data={
            "config": github_config.pk,
            "value_username": "octocat",
        },
    )

    assert response.status_code == 302
    assert SocialNetworkInstance.objects.filter(config=github_config).count() == 1
    vi = VariableInstance.objects.get(variable__identifier="username")
    assert vi.value == "octocat"


def test_dashboard_updates_variable_value(
    auth_client, user, github_config, username_variable
) -> None:
    instance = SocialNetworkInstance.objects.create(
        author=user, config=github_config
    )
    VariableInstance.objects.create(
        social_network_instance=instance,
        variable=username_variable,
        value="octocat",
    )

    response = auth_client.post(
        reverse(
            "profiles:dashboard_instance_edit", kwargs={"pk": instance.pk}
        ),
        data={"value_username": "newname"},
    )

    assert response.status_code == 302
    vi = VariableInstance.objects.get(
        social_network_instance=instance, variable=username_variable
    )
    assert vi.value == "newname"


def test_dashboard_archives_social_network_instance(
    auth_client, user, github_config, username_variable
) -> None:
    instance = SocialNetworkInstance.objects.create(
        author=user, config=github_config
    )
    VariableInstance.objects.create(
        social_network_instance=instance,
        variable=username_variable,
        value="octocat",
    )

    response = auth_client.post(
        reverse(
            "profiles:dashboard_instance_archive", kwargs={"pk": instance.pk}
        )
    )

    assert response.status_code == 302
    instance.refresh_from_db()
    assert instance.archived is True
    assert SocialNetworkInstance.objects.filter(pk=instance.pk).exists()


def test_dashboard_rejects_archiving_other_user_instance(
    auth_client, other_user, github_config
) -> None:
    other_instance = SocialNetworkInstance.objects.create(
        author=other_user, config=github_config
    )

    response = auth_client.post(
        reverse(
            "profiles:dashboard_instance_archive",
            kwargs={"pk": other_instance.pk},
        )
    )

    assert response.status_code in (302, 403, 404)
    other_instance.refresh_from_db()
    assert other_instance.archived is False


def test_dashboard_rejects_changing_instance_author(
    auth_client, user, other_user, github_config
) -> None:
    instance = SocialNetworkInstance.objects.create(
        author=other_user, config=github_config
    )

    response = auth_client.post(
        reverse(
            "profiles:dashboard_instance_edit", kwargs={"pk": instance.pk}
        ),
        data={"value_username": "newname", "author": user.pk},
    )

    assert response.status_code in (302, 403, 404)
    instance.refresh_from_db()
    assert instance.author_id == other_user.pk