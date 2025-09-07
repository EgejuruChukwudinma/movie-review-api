from django.contrib import admin
from .models import Review, Like

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "movie", "user", "rating", "created_at")
    search_fields = ("movie__title", "user__username")

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "review", "created_at")
    search_fields = ("user__username", "review__movie__title")

# Register your models here.
