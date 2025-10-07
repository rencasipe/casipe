from django.db import models

class ThematicCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Thematic Category"
        verbose_name_plural = "Thematic Categories"
        
    def save(self, *args, **kwargs):
        # Capitalize the first letter of the name
        if self.name and len(self.name) > 0:
            self.name = self.name[0].upper() + self.name[1:]
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

class Word(models.Model):
    # Gender choices 
    GENDER_CHOICES = [ ("M", "Masculine"), ("F", "Feminine"), ("N", "None"),]
    text = models.CharField(max_length=100)
    definition = models.TextField()
    
    # Many-to-many relationship with ThematicCategory
    thematic_categories = models.ManyToManyField(
        ThematicCategory,
        related_name="words",
        blank=True,
        help_text="Thematic categories this word belongs to",
    )
    # Gender fields
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default="N",
        help_text="Gender of the word (if applicable)",
    )
    has_gender = models.BooleanField(
        default=False, help_text="Check if this word has grammatical gender"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.has_gender and self.gender in ["M", "F"]:
            article = "el" if self.gender == "M" else "la"
            return f"{article} {self.text}"
        return self.text
    
    def save(self, *args, **kwargs):
        # Ensure consistency between has_gender and gender fields
        if self.gender != "N":
            self.has_gender = True
        elif not self.has_gender:
            self.gender = "N"
        super().save(*args, **kwargs)

class ExampleSentence(models.Model):
    word = models.ForeignKey( Word, on_delete=models.CASCADE, related_name="example_sentences" )
    text = models.TextField(help_text="The example sentence in Spanish")
    translation = models.TextField( blank=True, null=True, help_text="English translation of the example" )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Example for '{self.word.text}': {self.text[:50]}..."

