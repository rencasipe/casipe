# readers/models.py
from django.db import models

class DifficultyLevel(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Beginner", "Intermediate", "Advanced"
    level_number = models.PositiveSmallIntegerField(unique=True)  # e.g., 1, 2, 3
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} (Level {self.level_number})"
    
    class Meta:
        ordering = ['level_number']

class Reader(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    difficulty_level = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE, related_name='readers')
    description = models.TextField(help_text="Brief description or summary of the reader")
    content = models.TextField(help_text="The full text content of the reader")  # Added this field for the actual content
    publication_date = models.DateField()
    cover_image = models.ImageField(upload_to='reader_covers/', blank=True, null=True)
    word_count = models.PositiveIntegerField(help_text="Total words in the reader")
    vocabulary_focus = models.CharField(max_length=255, blank=True, help_text="Key vocabulary themes")
    grammar_focus = models.CharField(max_length=255, blank=True, help_text="Key grammar concepts")
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['difficulty_level__level_number', 'title']
