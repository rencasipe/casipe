from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),
    
    # Ckeditor 5    
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    
    # User management
    #path("accounts/", include("django.contrib.auth.urls")),
    
    # Local apps
    path("", include("pages.urls")),
    
    path("accounts/", include("accounts.urls")),
    path("blog/", include("blog.urls")),
    path("apps/", include("apps.urls")),    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


#if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
