from rest_framework import serializers
from .models import Movie

class MovieSerializer(serializers.ModelSerializer):
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Movie
        fields = ("id", "title", "description", "release_year", "genre", "created_at", "average_rating", "review_count")

