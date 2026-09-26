from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "age", "is_staff", "is_active")
    search_fields = ("full_name", "email")
    list_filter = ("is_staff", "is_active")