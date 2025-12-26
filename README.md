# Review API

<div align="center">

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DRF-ff1709?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

A production-ready REST API for reviewing places built with Django REST Framework. Allows users to register, authenticate, create reviews, and search places with advanced filtering capabilities.

[Features](#features) • [Installation](#installation) • [API Documentation](#api-documentation) • [Architecture](#architecture)

</div>

---

## Overview

The Review API is a RESTful web service that enables users to register with phone numbers, create reviews for various places (restaurants, clinics, shops), and search for places based on name and ratings. The system automatically creates places when submitting reviews and prevents duplicate reviews through database constraints.

## Features

**Authentication & User Management**
- Phone number-based registration and login
- Token-based stateless authentication
- Custom user model with phone validation

**Review Management**
- Create reviews with ratings (1-5 stars) and text
- Automatic place creation if non-existent
- One review per user per place constraint
- Reviews ordered by creation date

**Place Management**
- Search places by name with partial matching
- Filter by minimum average rating
- View detailed place information with all reviews
- User's own review prioritized in results

**Performance & Security**
- Query optimization with `select_related` and `prefetch_related`
- 5-minute TTL in-memory caching
- Database indexes on frequently queried fields
- Rate limiting (60 requests/minute per user)
- Input validation via serializers

## Technology Stack

| Category | Technology |
|----------|-----------|
| Framework | Django 4.2+, Django REST Framework 3.14+ |
| Database | SQLite3 (development), PostgreSQL/MySQL ready |
| Authentication | Token Authentication (DRF) |
| Language | Python 3.8+ |
| Testing Data | Faker |
| Caching | Django LocMemCache |

## Project Structure

```
Review_app/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── review_api/              # Project configuration
│   ├── settings.py          # Core settings
│   ├── urls.py              # URL routing
│   └── views.py             # API root
├── users/                   # Authentication app
│   ├── models.py            # Custom User model
│   ├── serializers.py       # User serializers
│   ├── views.py             # Register & Login views
│   └── migrations/
└── places/                  # Places & Reviews app
    ├── models.py            # Place & Review models
    ├── serializers.py       # Place/Review serializers
    ├── views.py             # API views
    ├── migrations/
    └── management/
        └── commands/
            └── seed_data.py # Database seeding
```

## Database Schema

**User Model**
```
- id (PK)
- name
- phone_number (Unique, Indexed)
- password (Hashed)
- created_at
- is_active, is_staff, is_superuser
```

**Place Model**
```
- id (PK)
- name (Indexed)
- address
- created_at
- Unique constraint: (name, address)
```

**Review Model**
```
- id (PK)
- rating (1-5)
- text
- user_id (FK to User, Indexed)
- place_id (FK to Place, Indexed)
- created_at
- Unique constraint: (user, place)
```

## Installation

**Prerequisites**
- Python 3.8+
- pip
- Virtual environment (recommended)

**Setup Steps**

1. Clone the repository
```bash
cd Review_app
```

2. Create and activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run migrations
```bash
python manage.py migrate
```

5. (Optional) Create superuser
```bash
python manage.py createsuperuser
```

6. (Optional) Seed test data
```bash
python manage.py seed_data --users 20 --places 30 --reviews 100
```

7. Start development server
```bash
python manage.py runserver
```

8. Access the API at `http://127.0.0.1:8000/`

## API Documentation

### Authentication Endpoints

**Register User**
```http
POST /api/register/
Content-Type: application/json

{
    "name": "John Doe",
    "phone_number": "+1234567890"
}
```

Response (201):
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": {
        "id": 1,
        "name": "John Doe",
        "phone_number": "+1234567890",
        "created_at": "2025-12-26T10:30:00Z"
    }
}
```

**Login**
```http
POST /api/login/
Content-Type: application/json

{
    "phone_number": "+1234567890"
}
```

Response (200):
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": { ... }
}
```

### Review Endpoints (Authentication Required)

**Create Review**
```http
POST /api/reviews/
Authorization: Token <your-token>
Content-Type: application/json

{
    "place_name": "Best Restaurant",
    "place_address": "123 Main St, City, State",
    "rating": 5,
    "text": "Amazing food and excellent service!"
}
```

Response (201):
```json
{
    "message": "Review created successfully",
    "review": {
        "id": 1,
        "rating": 5,
        "text": "Amazing food and excellent service!",
        "user_name": "John Doe",
        "created_at": "2025-12-26T11:00:00Z"
    },
    "place_id": 1
}
```

### Place Endpoints (Authentication Required)

**Search Places**
```http
GET /api/places/search/?name=restaurant&min_rating=4
Authorization: Token <your-token>
```

Query Parameters:
- `name` (optional): Search by place name (case-insensitive, partial match)
- `min_rating` (optional): Minimum average rating filter

Response (200):
```json
[
    {
        "id": 1,
        "name": "Best Restaurant",
        "average_rating": 4.5
    }
]
```

**Get Place Details**
```http
GET /api/places/1/
Authorization: Token <your-token>
```

Response (200):
```json
{
    "id": 1,
    "name": "Best Restaurant",
    "address": "123 Main St, City, State",
    "average_rating": 4.5,
    "created_at": "2025-12-26T10:00:00Z",
    "reviews": [
        {
            "id": 1,
            "rating": 5,
            "text": "Amazing food!",
            "user_name": "John Doe",
            "created_at": "2025-12-26T11:00:00Z"
        }
    ]
}
```

## Architecture

**Three-Tier Architecture**

1. **Presentation Layer**: RESTful API endpoints with DRF, token authentication, request/response serialization

2. **Business Logic Layer**: Custom serializers, view classes, permission classes, rate limiting, caching

3. **Data Layer**: SQLite/PostgreSQL, Django ORM, custom model managers, database constraints and indexes

**Design Patterns**
- MVT (Model-View-Template)
- Repository Pattern (Django ORM)
- Serializer Pattern
- Token Authentication Pattern

## Configuration

**Django REST Framework Settings**
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '60/minute',
    },
}
```

**Caching**
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
CACHE_TTL = 300  # 5 minutes
```

## Custom Management Commands

**Seed Database**
```bash
python manage.py seed_data --users <num> --places <num> --reviews <num>
```

Generates fake data using Faker library for testing and development.

Example:
```bash
python manage.py seed_data --users 50 --places 100 --reviews 500
```

## Testing

Test the API using Postman, cURL, or HTTPie.

**Example with cURL:**
```bash
# Register
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "phone_number": "+1234567890"}'

# Create Review
curl -X POST http://127.0.0.1:8000/api/reviews/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{"place_name": "Test Place", "place_address": "123 Test St", "rating": 5, "text": "Great!"}'
```

## Production Deployment

For production environments:
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Use environment variables for sensitive data
- Switch to PostgreSQL or MySQL
- Implement HTTPS
- Add security headers (HSTS, CSP)
- Configure logging and monitoring

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Faker Documentation](https://faker.readthedocs.io/)

---

<div align="center">
Built with Django REST Framework
</div>
