from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "movie", "user", "rating", "created_at")
    search_fields = ("movie__title", "user__username")

# Register your models here.
