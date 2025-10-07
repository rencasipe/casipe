from .views import SignupPageView
from django.urls import path

urlpatterns = [
    path("signup/", SignupPageView.as_view(), name="signup"),
        #path('accounts/', include('django.contrib.auth.urls')),
]
