from rest_framework import mixins, viewsets

from profiles.models import PublicProfile
from profiles.serializers import PublicProfileSerializer


class PublicProfileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = PublicProfile.objects.all()
    serializer_class = PublicProfileSerializer
    lookup_field = "public_username"
