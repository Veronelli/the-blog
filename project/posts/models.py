from django.db import models
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import User


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey["User"]("auth.User", on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return str(self.title)
