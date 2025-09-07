from django.contrib import admin
from .models import Review, Reaction

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "movie", "user", "rating", "created_at")
    search_fields = ("movie__title", "user__username")

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "review", "is_like", "created_at")
    search_fields = ("user__username", "review__movie__title")
    list_filter = ("is_like", "created_at")

# Register your models here.
