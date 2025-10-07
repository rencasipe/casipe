from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm

CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = [
        "email",
        "username",
        "is_superuser",
        "nickname", 
    ]
    
    # Add nickname to the fieldsets
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("nickname",)}),
    )
    
    # Add nickname to the add_fieldsets
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Custom Fields", {"fields": ("nickname",)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)