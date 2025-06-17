from django.urls import path

from .views import HomePageView, AppsPageView, AboutPageView, ProjectsPageView, ContactPageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("projects/", ProjectsPageView.as_view(), name="projects"),
    path("apps/", AppsPageView.as_view(), name="apps"),
    
    path("contact/", ContactPageView.as_view(), name="contact"),        
]