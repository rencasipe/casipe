from django.urls import path, include
from .views import HomePageView, AboutPageView, ProjectsPageView, ContactPageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("projects/", ProjectsPageView.as_view(), name="projects"),
    path("accounts/", include("accounts.urls")),
    
    path("contact/", ContactPageView.as_view(), name="contact"),        
]