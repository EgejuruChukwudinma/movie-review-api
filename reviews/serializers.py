from rest_framework import serializers
from .models import Review, Like

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    movie_title = serializers.ReadOnlyField(source="movie.title")
    likes_count = serializers.ReadOnlyField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ("id", "movie", "movie_title", "user", "rating", "content", "created_at", "updated_at", "likes_count", "liked")

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, attrs):
        # Check for unique constraint at serializer level
        if self.instance is None:  # Only for creation, not updates
            user = self.context['request'].user
            movie = attrs.get('movie')
            if Review.objects.filter(user=user, movie=movie).exists():
                raise serializers.ValidationError("You have already reviewed this movie.")
        return attrs

    def get_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

