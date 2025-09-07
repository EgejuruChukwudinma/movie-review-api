# Movie Review API

A comprehensive Django REST Framework API for managing movies, reviews, and user interactions. Built with JWT authentication, featuring likes, search, filtering, and pagination.

## Overview

This API allows users to:
- Register and authenticate with JWT tokens
- Create, read, update, and delete movies
- Write and manage movie reviews with ratings (1-5 stars)
- Like/unlike reviews and view top-liked content
- Search and filter movies and reviews
- Access paginated results with proper ordering

## Quickstart

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd movie-review-api
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
# DATABASE_URL=postgresql://user:password@localhost:5432/moviereviewdb

# JWT Settings (optional)
# JWT_ACCESS_TOKEN_LIFETIME=15
# JWT_REFRESH_TOKEN_LIFETIME=7
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register/` | Register new user | No |
| POST | `/auth/login/` | Login user | No |
| POST | `/auth/refresh/` | Refresh JWT token | No |
| GET | `/auth/profile/` | Get user profile | Yes |
| PATCH | `/auth/profile/` | Update user profile | Yes |
| DELETE | `/auth/profile/` | Delete user account | Yes |
| GET | `/auth/me/` | Get current user info | Yes |

### Movies

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/movies/` | List all movies with rating summary | No |
| POST | `/api/movies/` | Create new movie | Yes |
| GET | `/api/movies/{id}/` | Get movie details with rating summary | No |
| PUT/PATCH | `/api/movies/{id}/` | Update movie | Yes |
| DELETE | `/api/movies/{id}/` | Delete movie | Yes |

**Query Parameters:**
- `search`: Search by title or genre
- `genre`: Filter by genre
- `release_year`: Filter by release year
- `ordering`: Order by `title`, `release_year`, `created_at`, `average_rating`, `review_count`

**Response Fields:**
- `average_rating`: Average rating from all reviews (null if no reviews)
- `review_count`: Total number of reviews for the movie

### Reviews

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/reviews/` | List all reviews with reactions | No |
| POST | `/api/reviews/` | Create new review | Yes |
| GET | `/api/reviews/{id}/` | Get review details with reactions | No |
| PUT/PATCH | `/api/reviews/{id}/` | Update review | Yes (Owner only) |
| DELETE | `/api/reviews/{id}/` | Delete review | Yes (Owner only) |
| GET | `/api/reviews/by-movie/` | Get reviews by movie title | No |
| GET | `/api/reviews/top-liked/` | Get top-liked reviews | No |

**Query Parameters:**
- `search`: Search by movie title
- `movie`: Filter by movie ID
- `rating`: Filter by rating (1-5)
- `ordering`: Order by `rating`, `created_at`, `likes_count`, `dislikes_count`

**Response Fields:**
- `likes_count`: Number of likes for the review
- `dislikes_count`: Number of dislikes for the review
- `user_reaction`: Current user's reaction ("like", "dislike", or null)

### Reactions (Likes/Dislikes)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/reviews/{id}/like/` | Like a review (toggle if already liked) | Yes |
| POST | `/api/reviews/{id}/dislike/` | Dislike a review (toggle if already disliked) | Yes |
| GET | `/api/reviews/{id}/reactions/` | List all reactions (likes and dislikes) | No |

## API Usage Examples

### Authentication

**Register a new user:**
```bash
curl -X POST http://localhost:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password2": "securepassword123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

### Movies

**Create a movie:**
```bash
curl -X POST http://localhost:8000/api/movies/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Inception",
    "description": "A mind-bending thriller",
    "release_year": 2010,
    "genre": "Sci-Fi"
  }'
```

**Search movies:**
```bash
curl "http://localhost:8000/api/movies/?search=Inception"
```

### Reviews

**Create a review:**
```bash
curl -X POST http://localhost:8000/api/reviews/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "movie": 1,
    "rating": 5,
    "content": "Amazing movie with great plot twists!"
  }'
```

**Like a review:**
```bash
curl -X POST http://localhost:8000/api/reviews/1/like/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Dislike a review:**
```bash
curl -X POST http://localhost:8000/api/reviews/1/dislike/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Get all reactions for a review:**
```bash
curl "http://localhost:8000/api/reviews/1/reactions/"
```

**Get top-liked reviews:**
```bash
curl "http://localhost:8000/api/reviews/top-liked/"
```

**Get movies ordered by average rating:**
```bash
curl "http://localhost:8000/api/movies/?ordering=average_rating"
```

## Testing

Run the test suite:

```bash
python manage.py test
```

The test suite includes:
- Authentication tests (registration, login, profile management)
- Movie CRUD operations with rating summary and filtering
- Review CRUD operations with ownership validation
- Like/dislike functionality and reactions system
- Movie rating summary (average rating and review count)
- Pagination and search functionality
- Permission and validation tests

## Features

### Core Features
- ✅ JWT Authentication with refresh tokens
- ✅ Custom User model with email field
- ✅ Movies CRUD with search, filter, and ordering
- ✅ Reviews CRUD with owner-only edit/delete
- ✅ Rating validation (1-5 stars)
- ✅ Unique constraint (one review per user per movie)
- ✅ Pagination (10 items per page)
- ✅ Search and filtering capabilities
- ✅ **Movie rating summary (average rating + review count)**

### Advanced Features
- ✅ **Complete like/dislike system for reviews**
- ✅ Top-liked reviews endpoint
- ✅ Likes/dislikes count and user-specific reaction status
- ✅ **Movie rating analytics and ordering**
- ✅ Comprehensive test coverage (48 tests)
- ✅ Environment-based configuration
- ✅ Proper error handling and validation

### Security Features
- ✅ JWT token authentication
- ✅ Owner-only permissions for reviews
- ✅ Password validation
- ✅ Environment variable configuration
- ✅ Proper CORS handling ready

## Database Schema

### Users
- `id`, `username`, `email`, `password`, `date_joined`

### Movies
- `id`, `title`, `description`, `release_year`, `genre`, `created_at`

### Reviews
- `id`, `user`, `movie`, `rating`, `content`, `created_at`, `updated_at`
- Unique constraint: (user, movie)

### Reactions
- `id`, `user`, `review`, `is_like`, `created_at`
- Unique constraint: (user, review)
- `is_like`: Boolean field (True for like, False for dislike)

## Development

### Project Structure
```
movie-review-api/
├── accounts/          # User authentication and management
├── movies/           # Movie CRUD operations
├── reviews/          # Review CRUD and likes functionality
├── core/             # Django project settings
├── requirements.txt  # Python dependencies
├── .env             # Environment variables
└── README.md        # This file
```

### Adding New Features

1. Create models in the appropriate app
2. Create serializers for API representation
3. Create viewsets with proper permissions
4. Add URL patterns
5. Create and run migrations
6. Write comprehensive tests
7. Update documentation

## Deployment

For production deployment:

1. Set `DEBUG=False` in environment variables
2. Configure a production database (PostgreSQL recommended)
3. Set up static file serving
4. Configure proper `ALLOWED_HOSTS`
5. Use a production WSGI server (Gunicorn)
6. Set up reverse proxy (Nginx)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.

