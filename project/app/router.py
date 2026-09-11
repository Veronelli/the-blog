from django.conf import settings
from rest_framework.routers import DefaultRouter

from posts.views import PublicProfilePostViewSet
from profiles.views import PublicProfileViewSet

router = DefaultRouter(use_regex_path=False)
router.include_root_view = False
router.include_format_suffixes = settings.ENVIRONMENT == 'development'

router.register("authors", PublicProfileViewSet, basename="author")
router.register(
    "authors/<str:public_username>/posts",
    PublicProfilePostViewSet,
    basename="author-post",
)
