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

    fullname = serializers.SerializerMethodField()

    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}"