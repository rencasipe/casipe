from django.contrib import admin
from .models import DifficultyLevel, Reader

@admin.register(DifficultyLevel)
class DifficultyLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'level_number', 'description')
    search_fields = ('name',)

@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'difficulty_level', 'word_count', 'publication_date')
    list_filter = ('difficulty_level', 'publication_date')
    search_fields = ('title', 'author', 'description', 'content', 'vocabulary_focus', 'grammar_focus')
    
    # Split the admin form into multiple sections for better organization
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'difficulty_level', 'publication_date', 'cover_image')
        }),
        ('Content', {
            'fields': ('description', 'content'),
            'description': 'Enter the reader description and full text content here'
        }),
        ('Language Details', {
            'fields': ('word_count', 'vocabulary_focus', 'grammar_focus'),
            'description': 'Specify language learning details'
        }),
    )
