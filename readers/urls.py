# readers/urls.py
from django.urls import path
from . import views

app_name = 'readers'

urlpatterns = [
    path('', views.reader_list, name='reader_list'),
    path('<int:reader_id>/', views.reader_detail, name='reader_detail'),
]
