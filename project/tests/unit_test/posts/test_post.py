from posts.models import Post
from profiles.models import PublicProfile


def test_author_field_targets_public_profile() -> None:
    author = Post._meta.get_field("author")

    assert author.related_model is PublicProfile
    assert author.null is False
    assert author.remote_field.related_name == "posts"


def test_public_profile_exposes_posts_reverse_relation() -> None:
    posts_relation = PublicProfile._meta.get_field("posts")

    assert posts_relation.related_model is Post
    assert posts_relation.one_to_many is True


def test_post_keeps_assigned_public_profile_as_author() -> None:
    profile = PublicProfile(public_username="ada")
    post = Post(title="A post", content="Content", author=profile)

    assert post.author is profile
