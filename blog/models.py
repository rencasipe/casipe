from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    meta_description = models.CharField(max_length=160, blank=True)
    image = models.ImageField(upload_to="blog/images/", blank=True, null=True)
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(blank=True, null=True)
    reviewed = models.BooleanField(default=False)
    review_notes = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Custom save method to automatically set the published date.
        """
        # If the post is published and the published_date is not set, set it to the current time.
        if self.is_published and not self.published_date:
            self.published_date = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_scheduled(self):
        """
        Returns True if the post is marked as published but has a future published_date.
        """
        if self.is_published and self.published_date:
            return self.published_date > timezone.now()
        return False
    
    @property
    def is_live(self):
        """
        Returns True if the post is published and the published_date has passed.
        """
        if self.is_published and self.published_date:
            return self.published_date <= timezone.now()
        return False