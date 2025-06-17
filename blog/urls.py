from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog, name='blog'),
    path('post/<slug:slug>', views.post_page, name='post_page'),
    path('blog/search/', views.search_posts, name='search_posts'), 
]