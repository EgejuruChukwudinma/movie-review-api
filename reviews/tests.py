from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from movies.models import Movie
from .models import Review, Like

User = get_user_model()

class ReviewAPITestCase(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create test movie
        self.movie = Movie.objects.create(
            title='Test Movie',
            description='A test movie',
            release_year=2023,
            genre='Action'
        )
        
        # Create test review
        self.review = Review.objects.create(
            user=self.user1,
            movie=self.movie,
            rating=5,
            content='Great movie!'
        )
        
        # Get JWT token for user1
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_review_list_pagination(self):
        """Test that review list is paginated"""
        # Create additional movies and reviews to test pagination
        for i in range(15):
            movie = Movie.objects.create(
                title=f'Movie {i}',
                description=f'Description {i}',
                release_year=2023,
                genre='Action'
            )
            Review.objects.create(
                user=self.user1,
                movie=movie,
                rating=4,
                content=f'Review {i}'
            )
        
        url = reverse('review-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(len(response.data['results']), 10)  # PAGE_SIZE = 10

    def test_review_ordering_by_rating(self):
        """Test ordering reviews by rating"""
        # Create additional movies for different reviews
        movie2 = Movie.objects.create(title='Movie 2', description='Description 2', release_year=2023, genre='Action')
        movie3 = Movie.objects.create(title='Movie 3', description='Description 3', release_year=2023, genre='Action')
        
        # Create reviews with different ratings
        Review.objects.create(user=self.user1, movie=movie2, rating=1, content='Bad')
        Review.objects.create(user=self.user2, movie=movie3, rating=3, content='Average')
        
        url = reverse('review-list')
        response = self.client.get(url, {'ordering': 'rating'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ratings = [review['rating'] for review in response.data['results']]
        self.assertEqual(ratings, sorted(ratings))

    def test_review_search_by_movie_title(self):
        """Test searching reviews by movie title"""
        # Create another movie and review
        movie2 = Movie.objects.create(title='Another Movie', description='Another test')
        Review.objects.create(user=self.user2, movie=movie2, rating=4, content='Another review')
        
        url = reverse('review-list')
        response = self.client.get(url, {'search': 'Another'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['movie_title'], 'Another Movie')

    def test_review_like_toggle(self):
        """Test like/unlike functionality"""
        url = reverse('review-like', kwargs={'pk': self.review.pk})
        
        # Like the review
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['liked'])
        
        # Unlike the review
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])

    def test_review_likes_list(self):
        """Test listing users who liked a review"""
        # Create likes
        Like.objects.create(user=self.user1, review=self.review)
        Like.objects.create(user=self.user2, review=self.review)
        
        url = reverse('review-likes', kwargs={'pk': self.review.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 2)
        self.assertEqual(len(response.data['likers']), 2)

    def test_top_liked_reviews(self):
        """Test top-liked reviews endpoint"""
        # Create another movie and review
        movie2 = Movie.objects.create(title='Movie 2', description='Description 2', release_year=2023, genre='Action')
        review2 = Review.objects.create(
            user=self.user2,
            movie=movie2,
            rating=4,
            content='Another review'
        )
        
        # Add likes to reviews
        Like.objects.create(user=self.user1, review=self.review)
        Like.objects.create(user=self.user2, review=self.review)
        Like.objects.create(user=self.user1, review=review2)
        
        url = reverse('review-top-liked')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        # First review should have more likes
        self.assertEqual(response.data['results'][0]['likes_count'], 2)
        self.assertEqual(response.data['results'][1]['likes_count'], 1)

    def test_review_serializer_includes_likes_info(self):
        """Test that review serializer includes likes_count and liked fields"""
        # Add a like
        Like.objects.create(user=self.user1, review=self.review)
        
        url = reverse('review-detail', kwargs={'pk': self.review.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('likes_count', response.data)
        self.assertIn('liked', response.data)
        self.assertEqual(response.data['likes_count'], 1)
        self.assertTrue(response.data['liked'])

    def test_review_by_movie_endpoint(self):
        """Test the by-movie custom endpoint"""
        url = reverse('review-by-movie')
        response = self.client.get(url, {'title': 'Test Movie'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['movie_title'], 'Test Movie')

    def test_review_by_movie_endpoint_no_title(self):
        """Test the by-movie endpoint without title parameter"""
        url = reverse('review-by-movie')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_review_creation_requires_authentication(self):
        """Test that creating a review requires authentication"""
        self.client.credentials()  # Remove authentication
        
        url = reverse('review-list')
        data = {
            'movie': self.movie.id,
            'rating': 5,
            'content': 'Test review'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_update_requires_ownership(self):
        """Test that only review owner can update their review"""
        # Switch to user2
        refresh = RefreshToken.for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('review-detail', kwargs={'pk': self.review.pk})
        data = {'content': 'Updated content'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_review_delete_requires_ownership(self):
        """Test that only review owner can delete their review"""
        # Switch to user2
        refresh = RefreshToken.for_user(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('review-detail', kwargs={'pk': self.review.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_like_requires_authentication(self):
        """Test that liking a review requires authentication"""
        self.client.credentials()  # Remove authentication
        
        url = reverse('review-like', kwargs={'pk': self.review.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_rating_validation(self):
        """Test that rating must be between 1 and 5"""
        url = reverse('review-list')
        data = {
            'movie': self.movie.id,
            'rating': 6,  # Invalid rating
            'content': 'Test review'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)

    def test_unique_review_per_user_movie(self):
        """Test that a user can only have one review per movie"""
        # Try to create another review for the same movie by the same user
        url = reverse('review-list')
        data = {
            'movie': self.movie.id,
            'rating': 3,
            'content': 'Another review for same movie'
        }
        response = self.client.post(url, data)
        
        # Should get a 400 error due to unique constraint
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
