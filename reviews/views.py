from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsOwnerOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("user", "movie").all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filter by movie id and rating; search by movie title; order by rating/date
    filterset_fields = ["movie", "rating"]
    search_fields = ["movie__title"]
    ordering_fields = ["rating", "created_at"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="by-movie")
    def by_movie(self, request):
        """
        /api/reviews/by-movie?title=Inception
        """
        title = request.query_params.get("title")
        if not title:
            return Response({"detail": "Provide ?title=<movie title>."}, status=400)
        qs = self.get_queryset().filter(movie__title__iexact=title)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

# Create your views here.
