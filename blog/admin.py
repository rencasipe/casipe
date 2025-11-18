from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'author', 'reviewed', 'publication_status', 'has_audio_display', 'published_date', 'created_at', 'updated_at')
    list_filter = ('is_published', 'reviewed', 'created_at', 'updated_at')
    search_fields = ('title', 'subtitle', 'content', 'review_notes', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at', '-updated_at')
    readonly_fields = ('created_at', 'updated_at', 'publication_status_detail', 'audio_preview', 'has_audio_display')
    actions = ['unpublish_posts', 'publish_posts_now', 'mark_as_reviewed', 'mark_as_unreviewed']
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'subtitle', 'slug', 'content', 'meta_description', 'image', 'author')
        }),
        ('Audio Content', {
            'fields': ('audio_file', 'audio_duration', 'audio_preview', 'has_audio_display'),
            'description': 'Add audio content to your post. Supported formats: MP3, WAV, OGG, M4A, etc.'
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
    
    def has_audio_display(self, obj):
        """
        Display audio status with icon in list view and form.
        """
        if obj.has_audio:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">🎵 Yes</span>'
            )
        return format_html('<span style="color: #999;">❌ No</span>')
    
    has_audio_display.short_description = 'Has Audio'
    
    def audio_preview(self, obj):
        """
        Display audio player preview in the admin form.
        """
        if obj.audio_file:
            return format_html(
                '''
                <div style="margin-top: 10px;">
                    <audio controls style="width: 100%; max-width: 400px;">
                        <source src="{}" type="audio/mpeg">
                        Your browser does not support the audio element.
                    </audio>
                    <div style="margin-top: 5px;">
                        <small><strong>File:</strong> {}</small><br>
                        <small><strong>Size:</strong> {:.1f} MB</small>
                        {}
                    </div>
                </div>
                ''',
                obj.audio_file.url,
                obj.audio_file.name.split('/')[-1],  # Just show filename
                obj.audio_file.size / (1024 * 1024),  # Convert to MB
                f'<br><small><strong>Duration:</strong> {obj.audio_duration_formatted}</small>' if obj.audio_duration else ''
            )
        return format_html(
            '<span style="color: #999; font-style: italic;">No audio file uploaded</span>'
        )
    
    audio_preview.short_description = 'Audio Preview'
    
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