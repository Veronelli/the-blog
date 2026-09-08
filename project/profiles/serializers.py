from rest_framework import serializers

from profiles.models import PublicProfile


class PublicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicProfile
        fields = (
            "public_username",
            "first_name",
            "last_name",
            "title",
            "subtitle",
            "specialty",
            "short_description",
            "photo_url",
        )
