from django.conf import settings
from django.db import models
from movies.models import Movie
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        # Enforce at most one review per user per movie (adjust if you want multiple)
        constraints = [
            models.UniqueConstraint(fields=["user", "movie"], name="unique_review_per_user_movie")
        ]

    def __str__(self):
        return f"{self.user} → {self.movie} ({self.rating})"

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes")
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'review']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} likes {self.review}"

# Create your models here.
