from django.contrib import admin
from django.utils import timezone
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'reviewed', 'published_date', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'reviewed', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'review_notes', 'meta_description')  # Added meta_description to search fields
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at', '-updated_at')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['unpublish_posts', 'publish_posts', 'mark_as_reviewed', 'mark_as_unreviewed']
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'slug', 'content', 'meta_description', 'image', 'author')  # Added meta_description
        }),
        ('Review & Publication Settings', {
            'fields': ('is_published', 'published_date', 'reviewed', 'review_notes')
        }),
        ('Metadata', {
            'description': 'These fields are automatically managed by the system and cannot be edited directly.',
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def unpublish_posts(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} posts have been unpublished.')
    unpublish_posts.short_description = "Mark selected posts as unpublished"
    
    def publish_posts(self, request, queryset):
        updated = queryset.update(is_published=True, published_date=timezone.now())
        self.message_user(request, f'{updated} posts have been published.')
    publish_posts.short_description = "Mark selected posts as published"
    
    def mark_as_reviewed(self, request, queryset):
        updated = queryset.update(reviewed=True)
        self.message_user(request, f'{updated} posts have been marked as reviewed.')
    mark_as_reviewed.short_description = "Mark selected posts as reviewed"
    
    def mark_as_unreviewed(self, request, queryset):
        updated = queryset.update(reviewed=False)
        self.message_user(request, f'{updated} posts have been marked as unreviewed.')
    mark_as_unreviewed.short_description = "Mark selected posts as unreviewed"

admin.site.register(Post, PostAdmin)