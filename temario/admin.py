from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import ThematicCategory, Word, ExampleSentence
from django.contrib.admin import SimpleListFilter
from django.core.exceptions import ValidationError

class CategoryFilter(SimpleListFilter):
    title = 'Thematic Category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        categories = ThematicCategory.objects.all().order_by('name')
        return [(cat.id, cat.name) for cat in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(thematic_categories__id=self.value())
        return queryset

class ExampleSentenceInline(admin.StackedInline):
    model = ExampleSentence
    extra = 1
    fieldsets = (
        (None, {
            'fields': ('text',)
        }),
        ('Translation', {
            'fields': ('translation',),
            'classes': ('collapse',),
        }),
    )

@admin.register(ThematicCategory)
class ThematicCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'word_count')
    search_fields = ('name', 'description')
    list_filter = ('name',)
    readonly_fields = ('word_count',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(word_count=Count('words'))
        return queryset
    
    def word_count(self, obj):
        return obj.word_count
    word_count.short_description = 'Number of Words'
    word_count.admin_order_field = 'word_count'

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('display_text', 'contextual_definition', 'category_list', 'gender_display', 'created_at', 'example_count')
    list_filter = (CategoryFilter, 'gender', 'has_gender', 'created_at')
    search_fields = ('text', 'definition')
    filter_horizontal = ('thematic_categories',)
    date_hierarchy = 'created_at'
    inlines = [ExampleSentenceInline]
    
    fieldsets = (
        (None, {
            'fields': ('text',),
            'description': 'Enter the word. You can create multiple entries for the same word with different definitions.'
        }),
        ('Meaning in Context', {
            'fields': ('definition',),
            'description': 'Provide the definition for this word in the context of the selected categories.',
        }),
        ('Categories', {
            'fields': ('thematic_categories',),
            'description': 'Select the categories that apply to this specific definition of the word.',
        }),
        ('Gender Information', {
            'fields': ('has_gender', 'gender'),
            'description': 'Specify whether this word has grammatical gender and what it is',
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(example_count=Count('example_sentences'))
        queryset = queryset.prefetch_related('thematic_categories')
        return queryset
    
    def display_text(self, obj):
        if obj.has_gender and obj.gender in ["M", "F"]:
            article = "el" if obj.gender == "M" else "la"
            return f"{article} {obj.text}"
        return obj.text
    display_text.short_description = 'Word'
    
    def contextual_definition(self, obj):
        if obj.definition:
            definition_preview = obj.definition[:100] + "..." if len(obj.definition) > 100 else obj.definition
            return definition_preview
        return "—"
    contextual_definition.short_description = 'Definition'
    
    def category_list(self, obj):
        categories = obj.thematic_categories.all()
        if categories:
            # White text on black background
            return format_html(", ".join([
                f'<span style="background-color:#000000; color:#ffffff; padding:2px 5px; border-radius:3px; margin-right:3px;">{cat.name}</span>' 
                for cat in categories
            ]))
        return "—"
    category_list.short_description = 'Categories'
    
    def gender_display(self, obj):
        if not obj.has_gender:
            return "—"
        gender_map = {"M": "♂ Masculine", "F": "♀ Feminine", "N": "—"}
        return gender_map.get(obj.gender, "—")
    gender_display.short_description = 'Gender'
    
    def example_count(self, obj):
        return obj.example_count
    example_count.short_description = 'Examples'
    example_count.admin_order_field = 'example_count'
    
    def save_model(self, request, obj, form, change):
        if not obj.definition or obj.definition.strip() == '':
            raise ValidationError("A definition must be provided for this word.")
        
        # Remove any custom validation that prevents duplicate word text
        super().save_model(request, obj, form, change)
    
    actions = ['duplicate_word_entry']
    
    def duplicate_word_entry(self, request, queryset):
        for word in queryset:
            new_word = Word(
                text=word.text,
                definition="",  # Empty definition to be filled in
                has_gender=word.has_gender,
                gender=word.gender,
            )
            new_word.save()
            # Don't copy categories - these will be set differently
            self.message_user(request, f"Created a new entry for '{word.text}' - please add a definition and categories.")
    duplicate_word_entry.short_description = "Duplicate selected words for new context/meaning"

@admin.register(ExampleSentence)
class ExampleSentenceAdmin(admin.ModelAdmin):
    list_display = ('word_with_meaning', 'text_preview', 'has_translation', 'created_at')
    list_filter = ('word__thematic_categories', 'created_at')
    search_fields = ('text', 'translation', 'word__text', 'word__definition')
    autocomplete_fields = ['word']
    
    fieldsets = (
        (None, {
            'fields': ('word', 'text') 
        }),
        ('Translation', {
            'fields': ('translation',),
        }),
    )
    
    def text_preview(self, obj):
        if len(obj.text) > 75:
            return format_html("{}...", obj.text[:75])
        return obj.text
    text_preview.short_description = 'Example'
    
    def word_with_meaning(self, obj):
        word_text = obj.word.text
        if obj.word.has_gender and obj.word.gender in ["M", "F"]:
            article = "el" if obj.word.gender == "M" else "la"
            word_text = f"{article} {word_text}"
            
        # White text on black background for categories
        categories = obj.word.thematic_categories.all()
        if categories:
            category_html = format_html(", ".join([
                f'<span style="background-color:#000000; color:#ffffff; padding:1px 4px; border-radius:3px; font-size:0.9em;">{cat.name}</span>' 
                for cat in categories
            ]))
            category_display = format_html(" ({})", category_html)
        else:
            category_display = ""
            
        if obj.word.definition:
            definition_preview = obj.word.definition[:50] + "..." if len(obj.word.definition) > 50 else obj.word.definition
            return format_html("<strong>{}</strong>{} - {}", word_text, category_display, definition_preview)
        return format_html("<strong>{}</strong>{}", word_text, category_display)
    word_with_meaning.short_description = 'Word & Meaning'
    
    def has_translation(self, obj):
        return bool(obj.translation)
    has_translation.boolean = True
    has_translation.short_description = 'Has Translation'

# Customize admin site title, header and index title
admin.site.site_header = "Spanish Vocabulary Administration"
admin.site.site_title = "Spanish Vocabulary Admin Portal"
admin.site.index_title = "Welcome to Spanish Vocabulary Admin"
