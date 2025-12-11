from django import template
from django.conf import settings
import re

register = template.Library()

@register.filter(name='process_media')
def process_media(content):
    """
    Replace media placeholders with actual media URLs.
    Syntax: {{MEDIA:path/to/file.mp3}}
    Example: {{MEDIA:blog/audio/Estoy_comiendo.mp3}}
    """
    if not content:
        return content
    
    # Pattern to match {{MEDIA:path/to/file}}
    pattern = r'\{\{MEDIA:(.*?)\}\}'
    
    def replace_media(match):
        media_path = match.group(1).strip()
        media_url = settings.MEDIA_URL.rstrip('/')
        return f"{media_url}/{media_path}"
    
    processed_content = re.sub(pattern, replace_media, content)
    return processed_content