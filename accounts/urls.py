from .views import SignupPageView
from django.urls import path, include
urlpatterns = [
    path("signup/", SignupPageView.as_view(), name="signup"),
]