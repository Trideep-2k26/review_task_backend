from django.contrib import admin
from .models import Place, Review


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address', 'created_at']
    search_fields = ['name', 'address']
    ordering = ['-created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'place', 'rating', 'created_at']
    search_fields = ['user__name', 'place__name', 'text']
    list_filter = ['rating', 'created_at']
    ordering = ['-created_at']
    raw_id_fields = ['user', 'place']
