from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(
        "profiles.PublicProfile",
        on_delete=models.CASCADE,
        related_name="posts",
    )

    def __str__(self) -> str:
        return str(self.title)
