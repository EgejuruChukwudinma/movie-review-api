from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count
from .models import Movie
from .serializers import MovieSerializer

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    serializer_class = MovieSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["genre", "release_year"]
    search_fields = ["title", "genre"]
    ordering_fields = ["release_year", "created_at", "title", "average_rating", "review_count"]

    def get_queryset(self):
        return Movie.objects.annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )

# Create your views here.
