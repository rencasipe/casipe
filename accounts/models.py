from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        if self.nickname:
            return self.nickname
        return self.username