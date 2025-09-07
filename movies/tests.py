from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Movie

User = get_user_model()

class MovieAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.movie_data = {
            'title': 'Test Movie',
            'description': 'A test movie description',
            'release_year': 2023,
            'genre': 'Action'
        }

    def test_movie_list_pagination(self):
        """Test that movie list is paginated"""
        # Create additional movies to test pagination
        for i in range(15):
            Movie.objects.create(
                title=f'Movie {i}',
                description=f'Description {i}',
                release_year=2023,
                genre='Action'
            )
        
        url = reverse('movie-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(len(response.data['results']), 10)  # PAGE_SIZE = 10

    def test_movie_creation_requires_authentication(self):
        """Test that creating a movie requires authentication"""
        url = reverse('movie-list')
        response = self.client.post(url, self.movie_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_movie_creation_authenticated(self):
        """Test movie creation with authentication"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('movie-list')
        response = self.client.post(url, self.movie_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 1)
        self.assertEqual(Movie.objects.get().title, 'Test Movie')

    def test_movie_retrieve(self):
        """Test movie retrieval"""
        movie = Movie.objects.create(**self.movie_data)
        
        url = reverse('movie-detail', kwargs={'pk': movie.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Movie')

    def test_movie_update_requires_authentication(self):
        """Test that updating a movie requires authentication"""
        movie = Movie.objects.create(**self.movie_data)
        
        url = reverse('movie-detail', kwargs={'pk': movie.pk})
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_movie_update_authenticated(self):
        """Test movie update with authentication"""
        movie = Movie.objects.create(**self.movie_data)
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('movie-detail', kwargs={'pk': movie.pk})
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        movie.refresh_from_db()
        self.assertEqual(movie.title, 'Updated Title')

    def test_movie_delete_requires_authentication(self):
        """Test that deleting a movie requires authentication"""
        movie = Movie.objects.create(**self.movie_data)
        
        url = reverse('movie-detail', kwargs={'pk': movie.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_movie_delete_authenticated(self):
        """Test movie deletion with authentication"""
        movie = Movie.objects.create(**self.movie_data)
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('movie-detail', kwargs={'pk': movie.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Movie.objects.count(), 0)

    def test_movie_filtering_by_genre(self):
        """Test filtering movies by genre"""
        Movie.objects.create(title='Action Movie', genre='Action', release_year=2023)
        Movie.objects.create(title='Comedy Movie', genre='Comedy', release_year=2023)
        
        url = reverse('movie-list')
        response = self.client.get(url, {'genre': 'Action'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['genre'], 'Action')

    def test_movie_filtering_by_release_year(self):
        """Test filtering movies by release year"""
        Movie.objects.create(title='Old Movie', genre='Action', release_year=2020)
        Movie.objects.create(title='New Movie', genre='Action', release_year=2023)
        
        url = reverse('movie-list')
        response = self.client.get(url, {'release_year': 2023})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['release_year'], 2023)

    def test_movie_search_by_title(self):
        """Test searching movies by title"""
        Movie.objects.create(title='Inception', genre='Action', release_year=2010)
        Movie.objects.create(title='Interstellar', genre='Sci-Fi', release_year=2014)
        
        url = reverse('movie-list')
        response = self.client.get(url, {'search': 'Inception'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Inception')

    def test_movie_search_by_genre(self):
        """Test searching movies by genre"""
        Movie.objects.create(title='Action Movie', genre='Action', release_year=2023)
        Movie.objects.create(title='Comedy Movie', genre='Comedy', release_year=2023)
        
        url = reverse('movie-list')
        response = self.client.get(url, {'search': 'Action'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['genre'], 'Action')

    def test_movie_ordering_by_release_year(self):
        """Test ordering movies by release year"""
        Movie.objects.create(title='New Movie', genre='Action', release_year=2023)
        Movie.objects.create(title='Old Movie', genre='Action', release_year=2020)
        
        url = reverse('movie-list')
        response = self.client.get(url, {'ordering': 'release_year'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        years = [movie['release_year'] for movie in response.data['results']]
        self.assertEqual(years, sorted(years))

    def test_movie_ordering_by_title(self):
        """Test ordering movies by title"""
        Movie.objects.create(title='Zebra Movie', genre='Action', release_year=2023)
        Movie.objects.create(title='Alpha Movie', genre='Action', release_year=2023)
        
        url = reverse('movie-list')
        response = self.client.get(url, {'ordering': 'title'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [movie['title'] for movie in response.data['results']]
        self.assertEqual(titles, sorted(titles))

    def test_movie_ordering_by_created_at(self):
        """Test ordering movies by created_at"""
        movie1 = Movie.objects.create(title='First Movie', genre='Action', release_year=2023)
        movie2 = Movie.objects.create(title='Second Movie', genre='Action', release_year=2023)
        
        url = reverse('movie-list')
        response = self.client.get(url, {'ordering': 'created_at'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be ordered by created_at ascending (oldest first)
        self.assertEqual(response.data['results'][0]['title'], 'First Movie')
        self.assertEqual(response.data['results'][1]['title'], 'Second Movie')

    def test_movie_rating_summary(self):
        """Test that movies include average rating and review count"""
        from reviews.models import Review
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create a movie
        movie = Movie.objects.create(**self.movie_data)
        
        # Create reviews with different ratings from different users
        Review.objects.create(user=self.user, movie=movie, rating=5, content='Great!')
        Review.objects.create(user=user2, movie=movie, rating=3, content='Average')
        
        url = reverse('movie-detail', kwargs={'pk': movie.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('average_rating', response.data)
        self.assertIn('review_count', response.data)
        self.assertEqual(response.data['average_rating'], 4.0)  # (5+3)/2
        self.assertEqual(response.data['review_count'], 2)

    def test_movie_ordering_by_average_rating(self):
        """Test ordering movies by average rating"""
        from reviews.models import Review
        
        # Create movies
        movie1 = Movie.objects.create(title='Movie 1', genre='Action', release_year=2023)
        movie2 = Movie.objects.create(title='Movie 2', genre='Action', release_year=2023)
        
        # Add reviews with different average ratings
        Review.objects.create(user=self.user, movie=movie1, rating=5, content='Great!')
        Review.objects.create(user=self.user, movie=movie2, rating=3, content='Average')
        
        url = reverse('movie-list')
        response = self.client.get(url, {'ordering': 'average_rating'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be ordered by average rating ascending (lowest first)
        self.assertEqual(response.data['results'][0]['title'], 'Movie 2')
        self.assertEqual(response.data['results'][1]['title'], 'Movie 1')

    def test_movie_ordering_by_review_count(self):
        """Test ordering movies by review count"""
        from reviews.models import Review
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Create movies
        movie1 = Movie.objects.create(title='Movie 1', genre='Action', release_year=2023)
        movie2 = Movie.objects.create(title='Movie 2', genre='Action', release_year=2023)
        
        # Add different number of reviews from different users
        Review.objects.create(user=self.user, movie=movie1, rating=5, content='Great!')
        Review.objects.create(user=user2, movie=movie1, rating=4, content='Good!')
        Review.objects.create(user=self.user, movie=movie2, rating=3, content='Average')
        
        url = reverse('movie-list')
        response = self.client.get(url, {'ordering': 'review_count'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be ordered by review count ascending (lowest first)
        self.assertEqual(response.data['results'][0]['title'], 'Movie 2')
        self.assertEqual(response.data['results'][1]['title'], 'Movie 1')
