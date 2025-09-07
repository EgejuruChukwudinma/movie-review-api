from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Q
from .models import Review, Reaction
from .serializers import ReviewSerializer
from .permissions import IsOwnerOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related("user", "movie").annotate(
        likes_count=Count("reactions", filter=Q(reactions__is_like=True)),
        dislikes_count=Count("reactions", filter=Q(reactions__is_like=False))
    )
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filter by movie id and rating; search by movie title; order by rating/date
    filterset_fields = ["movie", "rating"]
    search_fields = ["movie__title"]
    ordering_fields = ["rating", "created_at", "likes_count", "dislikes_count"]

    def get_queryset(self):
        return Review.objects.select_related("user", "movie").annotate(
            likes_count=Count("reactions", filter=Q(reactions__is_like=True)),
            dislikes_count=Count("reactions", filter=Q(reactions__is_like=False))
        )

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
        POST /api/reviews/{id}/like/ - Like the review
        """
        review = self.get_object()
        user = request.user
        
        reaction, created = Reaction.objects.get_or_create(user=user, review=review)
        
        if not created:
            if reaction.is_like:
                # Already liked, remove the reaction
                reaction.delete()
                return Response({"reaction": None, "message": "Like removed"}, status=status.HTTP_200_OK)
            else:
                # Currently disliked, change to like
                reaction.is_like = True
                reaction.save()
                return Response({"reaction": "like", "message": "Changed to like"}, status=status.HTTP_200_OK)
        else:
            # New reaction, set as like
            reaction.is_like = True
            reaction.save()
            return Response({"reaction": "like", "message": "Like added"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def dislike(self, request, pk=None):
        """
        POST /api/reviews/{id}/dislike/ - Dislike the review
        """
        review = self.get_object()
        user = request.user
        
        reaction, created = Reaction.objects.get_or_create(user=user, review=review)
        
        if not created:
            if not reaction.is_like:
                # Already disliked, remove the reaction
                reaction.delete()
                return Response({"reaction": None, "message": "Dislike removed"}, status=status.HTTP_200_OK)
            else:
                # Currently liked, change to dislike
                reaction.is_like = False
                reaction.save()
                return Response({"reaction": "dislike", "message": "Changed to dislike"}, status=status.HTTP_200_OK)
        else:
            # New reaction, set as dislike
            reaction.is_like = False
            reaction.save()
            return Response({"reaction": "dislike", "message": "Dislike added"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def reactions(self, request, pk=None):
        """
        GET /api/reviews/{id}/reactions/ - List users who reacted to this review
        """
        review = self.get_object()
        reactions = review.reactions.select_related('user').all()
        
        likers = [{"id": r.user.id, "username": r.user.username, "reacted_at": r.created_at} 
                 for r in reactions if r.is_like]
        dislikers = [{"id": r.user.id, "username": r.user.username, "reacted_at": r.created_at} 
                    for r in reactions if not r.is_like]
        
        return Response({
            "review_id": review.id,
            "likes_count": len(likers),
            "dislikes_count": len(dislikers),
            "likers": likers,
            "dislikers": dislikers
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
