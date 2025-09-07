from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count
from .models import Review, Like
from .serializers import ReviewSerializer
from .permissions import IsOwnerOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("user", "movie").annotate(likes_count=Count("likes"))
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filter by movie id and rating; search by movie title; order by rating/date
    filterset_fields = ["movie", "rating"]
    search_fields = ["movie__title"]
    ordering_fields = ["rating", "created_at", "likes_count"]

    def get_queryset(self):
        return Review.objects.select_related("user", "movie").annotate(likes_count=Count("likes"))

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

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """
        POST /api/reviews/{id}/like/ - Toggle like for the review
        """
        review = self.get_object()
        user = request.user
        
        like, created = Like.objects.get_or_create(user=user, review=review)
        
        if not created:
            # Like already exists, so remove it
            like.delete()
            return Response({"liked": False, "message": "Like removed"}, status=status.HTTP_200_OK)
        else:
            return Response({"liked": True, "message": "Like added"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def likes(self, request, pk=None):
        """
        GET /api/reviews/{id}/likes/ - List users who liked this review
        """
        review = self.get_object()
        likes = review.likes.select_related('user').all()
        
        likers = [{"id": like.user.id, "username": like.user.username, "liked_at": like.created_at} for like in likes]
        
        return Response({
            "review_id": review.id,
            "likes_count": len(likers),
            "likers": likers
        })

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def top_liked(self, request):
        """
        GET /api/reviews/top-liked/ - Get reviews ordered by likes count descending
        """
        qs = self.get_queryset().order_by('-likes_count', '-created_at')
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

# Create your views here.
