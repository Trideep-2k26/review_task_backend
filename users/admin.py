from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'phone_number', 'created_at', 'is_active']
    search_fields = ['name', 'phone_number']
    list_filter = ['is_active', 'created_at']
    ordering = ['-created_at']
