from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from profiles.models import PublicProfile, SocialNetworkInstance


def public_profile(request: HttpRequest, public_username: str) -> HttpResponse:
    profile = get_object_or_404(PublicProfile, public_username=public_username)
    instances = SocialNetworkInstance.objects.filter(
        author=profile.user, archived=False
    )
    instance_urls = [
        {"instance": instance, "url": instance.url}
        for instance in instances
        if instance.url is not None
    ]
    return render(
        request,
        "profiles/public_profile.html",
        {
            "profile": profile,
            "instances": instances,
            "instance_urls": instance_urls,
        },
    )
