from profiles.serializers import PublicProfileSerializer
from tests.factories import create_public_profile


def test_public_profile_serializer_fullname() -> None:
    profile = create_public_profile(first_name="Octo", last_name="Cat")

    serialized = PublicProfileSerializer(profile).data

    assert serialized["fullname"] == "Octo Cat"
