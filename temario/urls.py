from django.urls import path
from .views import WordListView

app_name = 'temario'

urlpatterns = [
    path('', WordListView.as_view(), name='index'),
    # If using function-based view instead:
    # path('', views.index, name='index'),
]