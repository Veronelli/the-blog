from rest_framework.routers import DefaultRouter

from posts.views import PublicProfilePostViewSet
from profiles.views import PublicProfileViewSet

router = DefaultRouter(use_regex_path=False)
router.include_format_suffixes = False

router.register("authors", PublicProfileViewSet, basename="author")
router.register(
    "authors/<str:public_username>/posts",
    PublicProfilePostViewSet,
    basename="author-post",
)
