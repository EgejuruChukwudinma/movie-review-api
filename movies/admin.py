from django.contrib import admin
from .models import Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "genre", "release_year", "created_at")
    search_fields = ("title", "genre")

# Register your models here.
