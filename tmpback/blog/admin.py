from django.contrib import admin
from django.utils import timezone
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date', 'is_published', 'is_reviewed', 'reviewed_by', 'reviewed_at', 'created_at', 'updated_at')
    list_filter = ('is_published', 'is_reviewed', 'created_at', 'updated_at', 'reviewed_by')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at', '-updated_at')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at', 'reviewed_by')
    actions = ['unpublish_posts', 'publish_posts', 'mark_as_reviewed', 'mark_as_unreviewed']
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'slug', 'content', 'image', 'author')
        }),
        ('Publication Settings', {
            'fields': ('is_published', 'published_date')
        }),
        ('Review Status', {
            'fields': ('is_reviewed', 'reviewed_by', 'reviewed_at')
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
        current_time = timezone.now()
        updated = queryset.update(
            is_reviewed=True, 
            reviewed_by=request.user,
            reviewed_at=current_time
        )
        self.message_user(request, f'{updated} posts have been marked as reviewed.')
    mark_as_reviewed.short_description = "Mark selected posts as reviewed"
    
    def mark_as_unreviewed(self, request, queryset):
        updated = queryset.update(
            is_reviewed=False,
            reviewed_by=None,
            reviewed_at=None
        )
        self.message_user(request, f'{updated} posts have been marked as unreviewed.')
    mark_as_unreviewed.short_description = "Mark selected posts as not reviewed"

admin.site.register(Post, PostAdmin)
