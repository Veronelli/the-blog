from django.db import models
from django.utils.text import slugify


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    unique_name = models.SlugField(max_length=200, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(
        "profiles.PublicProfile",
        on_delete=models.CASCADE,
        related_name="posts",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("author", "unique_name"),
                name="post_author_unique_name",
            ),
        ]

    def save(self, *args: object, **kwargs: object) -> None:
        self.unique_name = slugify(self.title)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.title)
