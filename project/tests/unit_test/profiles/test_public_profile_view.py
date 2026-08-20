from __future__ import annotations

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
def client() -> Client:
    return Client()


@pytest.fixture
def user():
    user = create_user(username="alice", password="alice-password")
    user.set_password("alice-password")
    user.save()
    return user


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


@pytest.fixture
def profile(user):
    return create_public_profile(
        user=user,
        public_username="alice-public",
        first_name="Alice",
        last_name="Smith",
        title="Engineer",
        subtitle="Hello world",
        specialty="Backend",
        short_description="About me.",
        photo_url="https://example.test/alice.png",
    ).save() or PublicProfile.objects.get(user=user)


def test_public_profile_view_returns_404_for_unknown_username(client) -> None:
    response = client.get(
        reverse("profiles:public_profile", kwargs={"public_username": "ghost"})
    )

    assert response.status_code == 404


def test_public_profile_view_renders_200_for_existing_username(client, profile) -> None:
    response = client.get(
        reverse(
            "profiles:public_profile",
            kwargs={"public_username": profile.public_username},
        )
    )

    assert response.status_code == 200


def test_public_profile_view_exposes_public_fields(client, profile) -> None:
    response = client.get(
        reverse(
            "profiles:public_profile",
            kwargs={"public_username": profile.public_username},
        )
    )

    context_profile = response.context["profile"]
    assert context_profile.pk == profile.pk
    assert context_profile.public_username == "alice-public"
    assert context_profile.first_name == "Alice"
    assert context_profile.title == "Engineer"


def test_public_profile_view_renders_photo_url_in_context(
    client, profile
) -> None:
    response = client.get(
        reverse(
            "profiles:public_profile",
            kwargs={"public_username": profile.public_username},
        )
    )

    assert response.context["profile"].photo_url == "https://example.test/alice.png"


def test_public_profile_view_only_exposes_active_instances(
    client, profile, user, github_config, username_variable
) -> None:
    active = SocialNetworkInstance.objects.create(author=user, config=github_config)
    VariableInstance.objects.create(
        social_network_instance=active,
        variable=username_variable,
        value="octocat",
    )
    archived = SocialNetworkInstance.objects.create(
        author=user, config=github_config, archived=True
    )
    VariableInstance.objects.create(
        social_network_instance=archived,
        variable=username_variable,
        value="archived-user",
    )

    response = client.get(
        reverse(
            "profiles:public_profile",
            kwargs={"public_username": profile.public_username},
        )
    )

    instances = list(response.context["instances"])
    assert active in instances
    assert archived not in instances


def test_public_profile_view_exposes_constructed_urls(
    client, profile, user, github_config, username_variable
) -> None:
    instance = SocialNetworkInstance.objects.create(
        author=user, config=github_config
    )
    VariableInstance.objects.create(
        social_network_instance=instance,
        variable=username_variable,
        value="octocat",
    )

    response = client.get(
        reverse(
            "profiles:public_profile",
            kwargs={"public_username": profile.public_username},
        )
    )

    instance_urls = {
        item["instance"].pk: item["url"]
        for item in response.context["instance_urls"]
    }
    assert instance_urls[instance.pk] == "https://github.com/octocat"


def test_public_profile_view_omits_instances_without_url(
    client, profile, user, github_config, username_variable
) -> None:
    instance = SocialNetworkInstance.objects.create(
        author=user, config=github_config
    )
    VariableInstance.objects.create(
        social_network_instance=instance,
        variable=username_variable,
        value="",
    )

    response = client.get(
        reverse(
            "profiles:public_profile",
            kwargs={"public_username": profile.public_username},
        )
    )

    instance_pks = {item["instance"].pk for item in response.context["instance_urls"]}
    assert instance.pk not in instance_pks