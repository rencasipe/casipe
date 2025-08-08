# readers/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Reader, DifficultyLevel

def reader_list(request):
    # Get all difficulty levels for filtering
    difficulty_levels = DifficultyLevel.objects.all()
    
    # Initial queryset
    readers = Reader.objects.all()
    
    # Get search query
    search_query = request.GET.get('search', '')
    level_filter = request.GET.get('level', '')
    
    # Apply search filter if provided
    if search_query:
        readers = readers.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(content__icontains=search_query) |  # Added content to search
            Q(vocabulary_focus__icontains=search_query) |
            Q(grammar_focus__icontains=search_query)
        )
    
    # Apply difficulty level filter if provided
    if level_filter:
        readers = readers.filter(difficulty_level__level_number=level_filter)
    
    context = {
        'readers': readers,
        'difficulty_levels': difficulty_levels,
        'search_query': search_query,
        'level_filter': level_filter,
    }
    
    return render(request, 'readers/reader_list.html', context)

def reader_detail(request, reader_id):
    reader = get_object_or_404(Reader, id=reader_id)
    
    # Get related readers with the same difficulty level
    related_readers = Reader.objects.filter(
        difficulty_level=reader.difficulty_level
    ).exclude(id=reader.id)[:4]
    
    context = {
        'reader': reader,
        'related_readers': related_readers,
    }
    
    return render(request, 'readers/reader_detail.html', context)
