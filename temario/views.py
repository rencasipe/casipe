# views.py
from django.views.generic import ListView
from django.db.models import Q
from .models import Word, ThematicCategory

class WordListView(ListView):
    model = Word
    template_name = 'temario/index.html'
    context_object_name = 'words'
    paginate_by = 12  # Show 12 words per page
    
    def get_queryset(self):
        queryset = Word.objects.all().order_by('text')
        
        # Apply search filter if provided
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(text__icontains=search_query) |
                Q(definition__icontains=search_query)
            )
        
        # Apply category filter if provided
        category_id = self.request.GET.get('category', '')
        if category_id and category_id.isdigit():
            queryset = queryset.filter(thematic_categories__id=category_id)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add all thematic categories for the dropdown filter
        context['thematic_categories'] = ThematicCategory.objects.all().order_by('name')
        
        # Add selected category for display of category description
        category_id = self.request.GET.get('category', '')
        if category_id and category_id.isdigit():
            context['selected_category'] = ThematicCategory.objects.filter(id=category_id).first()
            
        return context
