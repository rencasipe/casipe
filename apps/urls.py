from django.urls import path, include
from .views import AppsPageView

urlpatterns = [
    path("", AppsPageView.as_view(), name="apps"),
    path('temario/', include('temario.urls')),
    path('lector/', include('readers.urls')),    
]