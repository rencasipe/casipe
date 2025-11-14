from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'reviewed', 'publication_status', 'published_date', 'created_at', 'updated_at')
    list_filter = ('is_published', 'reviewed', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'review_notes', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at', '-updated_at')
    readonly_fields = ('created_at', 'updated_at', 'publication_status_detail')
    actions = ['unpublish_posts', 'publish_posts_now', 'mark_as_reviewed', 'mark_as_unreviewed']
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'slug', 'content', 'meta_description', 'image', 'author')
        }),
        ('Review & Publication Settings', {
            'fields': ('is_published', 'published_date', 'publication_status_detail', 'reviewed', 'review_notes'),
            'description': 'Set a future date to schedule the post. Past or current dates will publish immediately.'
        }),
        ('Metadata', {
            'description': 'These fields are automatically managed by the system and cannot be edited directly.',
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def publication_status(self, obj):
        """
        Display publication status with color coding in the list view.
        """
        if not obj.is_published:
            return format_html('<span style="color: #999;">Unpublished</span>')
        elif obj.is_scheduled:
            return format_html('<span style="color: #F1BF00; font-weight: bold;">⏰ Scheduled</span>')
        elif obj.is_live:
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Live</span>')
        return format_html('<span style="color: #999;">Unknown</span>')
    
    publication_status.short_description = 'Status'
    
    def publication_status_detail(self, obj):
        """
        Display detailed publication status information in the form.
        """
        if not obj.is_published:
            return format_html('<span style="color: #999;">This post is not published.</span>')
        elif obj.is_scheduled:
            return format_html(
                '<span style="color: #F1BF00; font-weight: bold;">⏰ Scheduled for: {}</span><br>'
                '<small>This post will automatically become live at the scheduled time.</small>',
                obj.published_date.strftime('%B %d, %Y at %I:%M %p')
            )
        elif obj.is_live:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Live since: {}</span>',
                obj.published_date.strftime('%B %d, %Y at %I:%M %p')
            )
        return format_html('<span style="color: #999;">Status unknown</span>')
    
    publication_status_detail.short_description = 'Publication Status'
    
    def unpublish_posts(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} posts have been unpublished.')
    unpublish_posts.short_description = "Mark selected posts as unpublished"
    
    def publish_posts_now(self, request, queryset):
        updated = queryset.update(is_published=True, published_date=timezone.now())
        self.message_user(request, f'{updated} posts have been published immediately.')
    publish_posts_now.short_description = "Publish selected posts now"
    
    def mark_as_reviewed(self, request, queryset):
        updated = queryset.update(reviewed=True)
        self.message_user(request, f'{updated} posts have been marked as reviewed.')
    mark_as_reviewed.short_description = "Mark selected posts as reviewed"
    
    def mark_as_unreviewed(self, request, queryset):
        updated = queryset.update(reviewed=False)
        self.message_user(request, f'{updated} posts have been marked as unreviewed.')
    mark_as_unreviewed.short_description = "Mark selected posts as unreviewed"

admin.site.register(Post, PostAdmin)