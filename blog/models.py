from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# ========================================
# MAIN POST MODEL
# ========================================
class Post(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=250, blank=True, help_text="Optional subtitle or tagline")
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(
        max_length=500, 
        blank=True, 
        help_text="Brief summary or teaser of the post (max 500 characters)"
    )    
    content = models.TextField()
    meta_description = models.CharField(max_length=160, blank=True)
    image = models.ImageField(upload_to="blog/images/", blank=True, null=True)
    
    # Main audio field (optional - you can keep this or remove it)
    audio_file = models.FileField(
        upload_to="blog/audio/",
        blank=True, 
        null=True,
        help_text="Upload an audio file"
    )
    audio_duration = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        help_text="Duration in seconds"
    )
    
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

    @property
    def has_audio(self):
        """
        Returns True if the post has any audio files attached.
        """
        return bool(self.audio_file) or self.audio_files.exists()

    @property
    def audio_duration_formatted(self):
        """Return duration in MM:SS format"""
        if self.audio_duration:
            minutes = self.audio_duration // 60
            seconds = self.audio_duration % 60
            return f"{minutes}:{seconds:02d}"
        return None


# ========================================
# RELATED AUDIO MODEL (NEW!)
# ========================================
class PostAudio(models.Model):
    """
    Multiple audio files can be attached to a single post.
    This allows unlimited audio files per post.
    """
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='audio_files'  # Access via: post.audio_files.all()
    )
    title = models.CharField(
        max_length=200, 
        help_text="e.g., 'Estoy comiendo', 'Example 1', 'Pronunciation'"
    )
    audio_file = models.FileField(
        upload_to="blog/audio/",
        help_text="Upload audio file (MP3, WAV, OGG, M4A)"
    )
    audio_duration = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        help_text="Duration in seconds (optional)"
    )
    description = models.CharField(
        max_length=500,
        blank=True,
        help_text="Optional description or context for this audio"
    )
    order = models.PositiveIntegerField(
        default=0, 
        help_text="Display order (lower numbers appear first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Post Audio File"
        verbose_name_plural = "Post Audio Files"

    def __str__(self):
        return f"{self.post.title} - {self.title}"

    @property
    def audio_duration_formatted(self):
        """Return duration in MM:SS format"""
        if self.audio_duration:
            minutes = self.audio_duration // 60
            seconds = self.audio_duration % 60
            return f"{minutes}:{seconds:02d}"
        return None
    
    @property
    def file_path_for_content(self):
        """
        Returns the path to use in content field.
        Example: 'blog/audio/Estoy_comiendo.mp3'
        """
        if self.audio_file:
            # Return the path without 'media/' prefix
            return str(self.audio_file.name)
        return ""