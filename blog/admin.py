from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Post, PostAudio


# ========================================
# INLINE FOR MULTIPLE AUDIO FILES
# ========================================
class PostAudioInline(admin.TabularInline):
    """
    Inline admin for adding multiple audio files to a post.
    """
    model = PostAudio
    extra = 2  # Show 2 empty forms by default
    fields = ('title', 'audio_file', 'audio_duration', 'description', 'order', 'audio_preview', 'copy_path_button')
    readonly_fields = ('audio_preview', 'copy_path_button')
    
    def audio_preview(self, obj):
        """Display audio player preview"""
        if obj.audio_file:
            return format_html(
                '''
                <audio controls style="width: 250px;">
                    <source src="{}" type="audio/mpeg">
                </audio>
                <br><small>{:.1f} MB</small>
                ''',
                obj.audio_file.url,
                obj.audio_file.size / (1024 * 1024)
            )
        return format_html('<span style="color: #999;">No file</span>')
    
    audio_preview.short_description = 'Preview'
    
    def copy_path_button(self, obj):
        """Button to copy the path for use in content"""
        if obj.audio_file:
            path = obj.file_path_for_content
            return format_html(
                '''
                <button type="button" 
                        onclick="navigator.clipboard.writeText('{{{{MEDIA:{}}}}}'); alert('Copied to clipboard: {{{{MEDIA:{}}}}}');"
                        style="padding: 5px 10px; background: #417690; color: white; border: none; border-radius: 3px; cursor: pointer;">
                    📋 Copy
                </button>
                <br><small style="color: #666; display: block; margin-top: 3px;"><code>{{{{MEDIA:{}}}}}</code></small>
                ''',
                path,
                path,
                path
            )
        return ''
    
    copy_path_button.short_description = 'Use in Content'


# ========================================
# MAIN POST ADMIN
# ========================================
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'excerpt_preview', 
        'author', 
        'reviewed', 
        'publication_status', 
        'audio_count_display', 
        'published_date', 
        'created_at', 
        'updated_at'
    )
    list_filter = ('is_published', 'reviewed', 'created_at', 'updated_at')
    search_fields = ('title', 'subtitle', 'excerpt', 'content', 'review_notes', 'meta_description')
    #prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at', '-updated_at')
    readonly_fields = (
        'created_at', 
        'updated_at', 
        'publication_status_detail', 
        'audio_preview', 
        'audio_count_display', 
        'all_audio_files_display'
    )
    actions = [
        'unpublish_posts', 
        'publish_posts_now', 
        'mark_as_reviewed', 
        'mark_as_unreviewed'
    ]
    
    # Add the inline for multiple audio files
    inlines = [PostAudioInline]
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'subtitle', 'slug', 'excerpt', 'content', 'meta_description', 'image', 'author'),
            'description': '''
                <div style="background: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; margin-bottom: 15px;">
                    <strong style="color: #1976D2;">💡 How to Use Audio in Content:</strong><br>
                    <ol style="margin: 10px 0 0 0; padding-left: 20px;">
                        <li>Scroll down to <strong>"Post audio files"</strong> section</li>
                        <li>Upload your audio files there</li>
                        <li>Click the <strong>📋 Copy</strong> button next to each audio file</li>
                        <li>Paste the copied code into your Content field above</li>
                    </ol>
                    <p style="margin: 10px 0 0 0;"><strong>Example:</strong> 
                    <code>&lt;audio controls&gt;&lt;source src="{{MEDIA:blog/audio/file.mp3}}"&gt;&lt;/audio&gt;</code></p>
                </div>
            '''
        }),
        ('Main Audio Content (Optional - Legacy)', {
            'fields': ('audio_file', 'audio_duration', 'audio_preview'),
            'description': 'Optional main audio file. <strong>Recommended:</strong> Use "Post audio files" section below instead for better organization.',
            'classes': ('collapse',)
        }),
        ('All Audio Files Summary', {
            'fields': ('audio_count_display', 'all_audio_files_display'),
            'description': 'Quick reference for all audio files attached to this post.',
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
    
    # ========================================
    # LIST DISPLAY METHODS
    # ========================================
    
    def excerpt_preview(self, obj):
        """Display a truncated excerpt in the list view."""
        if obj.excerpt:
            if len(obj.excerpt) > 75:
                return f"{obj.excerpt[:75]}..."
            return obj.excerpt
        return format_html('<span style="color: #999; font-style: italic;">No excerpt</span>')
    
    excerpt_preview.short_description = 'Excerpt'
    
    def publication_status(self, obj):
        """Display publication status with color coding in the list view."""
        if not obj.is_published:
            return format_html('<span style="color: #999;">Unpublished</span>')
        elif obj.is_scheduled:
            return format_html('<span style="color: #F1BF00; font-weight: bold;">⏰ Scheduled</span>')
        elif obj.is_live:
            return format_html('<span style="color: #28a745; font-weight: bold;">✓ Live</span>')
        return format_html('<span style="color: #999;">Unknown</span>')
    
    publication_status.short_description = 'Status'
    
    def audio_count_display(self, obj):
        """Display count of audio files"""
        count = obj.audio_files.count()
        if obj.audio_file:
            count += 1
        
        if count > 0:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">🎵 {} file{}</span>',
                count,
                's' if count != 1 else ''
            )
        return format_html('<span style="color: #999;">❌ No audio</span>')
    
    audio_count_display.short_description = 'Audio Files'
    
    # ========================================
    # FORM DISPLAY METHODS
    # ========================================
    
    def all_audio_files_display(self, obj):
        """Display all audio files with copy buttons"""
        html_parts = []
        
        # Main audio file (legacy)
        if obj.audio_file:
            path = str(obj.audio_file.name)
            html_parts.append(format_html(
                '''
                <div style="margin: 10px 0; padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px;">
                    <strong style="color: #856404;">📁 Main Audio (Legacy):</strong><br>
                    <audio controls style="width: 100%; max-width: 400px; margin: 10px 0;">
                        <source src="{}" type="audio/mpeg">
                    </audio><br>
                    <small style="color: #666;"><strong>File:</strong> {}</small><br>
                    <button type="button" 
                            onclick="navigator.clipboard.writeText('{{{{MEDIA:{}}}}}'); alert('✓ Copied to clipboard!');"
                            style="padding: 8px 15px; background: #417690; color: white; border: none; border-radius: 4px; cursor: pointer; margin-top: 8px; font-weight: 500;">
                        📋 Copy Path for Content
                    </button>
                    <div style="margin-top: 8px; padding: 8px; background: #f8f9fa; border-radius: 3px;">
                        <small style="font-family: monospace; color: #495057;">{{{{MEDIA:{}}}}}</small>
                    </div>
                </div>
                ''',
                obj.audio_file.url,
                obj.audio_file.name.split('/')[-1],
                path,
                path
            ))
        
        # Additional audio files
        audio_files = obj.audio_files.all()
        if audio_files:
            for idx, audio in enumerate(audio_files, 1):
                path = audio.file_path_for_content
                html_parts.append(format_html(
                    '''
                    <div style="margin: 10px 0; padding: 15px; background: #d4edda; border-left: 4px solid #28a745; border-radius: 4px;">
                        <strong style="color: #155724;">🎵 Audio File #{}: {}</strong>
                        {}<br>
                        <audio controls style="width: 100%; max-width: 400px; margin: 10px 0;">
                            <source src="{}" type="audio/mpeg">
                        </audio><br>
                        <small style="color: #666;"><strong>File:</strong> {}</small>
                        {}<br>
                        <button type="button" 
                                onclick="navigator.clipboard.writeText('{{{{MEDIA:{}}}}}'); alert('✓ Copied to clipboard!');"
                                style="padding: 8px 15px; background: #417690; color: white; border: none; border-radius: 4px; cursor: pointer; margin-top: 8px; font-weight: 500;">
                            📋 Copy Path for Content
                        </button>
                        <div style="margin-top: 8px; padding: 8px; background: #f8f9fa; border-radius: 3px;">
                            <small style="font-family: monospace; color: #495057;">{{{{MEDIA:{}}}}}</small>
                        </div>
                    </div>
                    ''',
                    idx,
                    audio.title,
                    f'<br><small style="color: #666;"><em>{audio.description}</em></small>' if audio.description else '',
                    audio.audio_file.url,
                    audio.audio_file.name.split('/')[-1],
                    f'<br><small style="color: #666;"><strong>Duration:</strong> {audio.audio_duration_formatted}</small>' if audio.audio_duration else '',
                    path,
                    path
                ))
        
        if not html_parts:
            return format_html(
                '''
                <div style="padding: 20px; background: #f8f9fa; border: 2px dashed #dee2e6; border-radius: 4px; text-align: center;">
                    <p style="color: #6c757d; margin: 0; font-size: 14px;">
                        📝 No audio files uploaded yet. Scroll down to <strong>"Post audio files"</strong> section to add audio.
                    </p>
                </div>
                '''
            )
        
        return format_html(''.join(str(part) for part in html_parts))
    
    all_audio_files_display.short_description = 'Audio Files Reference'
    
    def audio_preview(self, obj):
        """Display audio player preview in the admin form."""
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
                obj.audio_file.name.split('/')[-1],
                obj.audio_file.size / (1024 * 1024),
                f'<br><small><strong>Duration:</strong> {obj.audio_duration_formatted}</small>' if obj.audio_duration else ''
            )
        return format_html(
            '<span style="color: #999; font-style: italic;">No audio file uploaded</span>'
        )
    
    audio_preview.short_description = 'Audio Preview'
    
    def publication_status_detail(self, obj):
        """Display detailed publication status information in the form."""
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
    
    # ========================================
    # ADMIN ACTIONS
    # ========================================
    
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


# ========================================
# STANDALONE POSTAUDIO ADMIN (Optional)
# ========================================
class PostAudioAdmin(admin.ModelAdmin):
    """
    Standalone admin for PostAudio if you want to manage audio files separately.
    This is optional - you can remove it if you only want inline editing.
    """
    list_display = ('title', 'post', 'audio_file', 'audio_duration', 'order', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ('title', 'description', 'post__title')
    ordering = ('post', 'order', 'created_at')
    readonly_fields = ('created_at', 'audio_preview')
    
    fields = ('post', 'title', 'audio_file', 'audio_preview', 'audio_duration', 'description', 'order', 'created_at')
    
    def audio_preview(self, obj):
        """Display audio player preview"""
        if obj.audio_file:
            return format_html(
                '''
                <audio controls style="width: 100%; max-width: 400px;">
                    <source src="{}" type="audio/mpeg">
                </audio>
                <p><small><strong>File:</strong> {}</small><br>
                <small><strong>Size:</strong> {:.1f} MB</small></p>
                ''',
                obj.audio_file.url,
                obj.audio_file.name.split('/')[-1],
                obj.audio_file.size / (1024 * 1024)
            )
        return format_html('<span style="color: #999;">No file</span>')
    
    audio_preview.short_description = 'Preview'


# ========================================
# REGISTER MODELS
# ========================================
admin.site.register(Post, PostAdmin)
admin.site.register(PostAudio, PostAudioAdmin)  # Optional: remove this line if you don't want standalone audio admin