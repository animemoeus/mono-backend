# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based backend mono-repository for AnimeMoeUs services, including multiple microservices and APIs:

- **Backend**: Core Django application with user management, authentication
- **CineMatch**: Movie recommendation system with vector search using pgvector
- **Discord**: Discord bot integration and URL refresh services
- **Instagram**: Instagram user/story monitoring and API integration
- **NZ Store**: Product catalog and order management system
- **TikTok**: TikTok video monitoring and user tracking
- **Twitter Downloader**: Twitter video download bot and web interface
- **Waifu**: Image generation and Discord/Telegram bot services

## Development Commands

### Local Development with Docker
```bash
# Start all services
docker-compose -f local.yml up

# Start specific service
docker-compose -f local.yml up django
docker-compose -f local.yml up postgres redis

# Access Django shell
docker-compose -f local.yml exec django python manage.py shell

# Run migrations
docker-compose -f local.yml exec django python manage.py migrate

# Create superuser
docker-compose -f local.yml exec django python manage.py createsuperuser
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
coverage run -m pytest
coverage html

# Run specific test file
pytest backend/users/tests/test_models.py

# Run tests for specific app
pytest instagram/tests/
```

### Code Quality
```bash
# Format code with black
black .

# Check imports with isort
isort .

# Lint with flake8
flake8

# Type checking with mypy
mypy backend

# Run all pre-commit hooks
pre-commit run --all-files

# Template linting (commented out in pre-commit)
djlint --reformat-django templates/
djlint templates/
```

### Database Operations
```bash
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load initial data
python manage.py loaddata fixtures/initial_data.json

# Run custom scripts (django-extensions)
python manage.py runscript scripts.arter
```

### Celery Operations
```bash
# Start celery worker (from backend/ directory)
cd backend
celery -A config.celery_app worker -l info

# Start celery beat scheduler
celery -A config.celery_app beat

# Start worker with beat embedded (development only)
celery -A config.celery_app worker -B -l info

# Monitor with flower
# Access at http://localhost:5555 when using docker-compose
```

## Architecture Overview

### Project Structure
- `backend/`: Core Django app with users, authentication, utilities
- `config/`: Django settings, URL routing, Celery configuration
- `requirements/`: Separated requirements files (base, local, production)
- `compose/`: Docker configurations for local and production
- `scripts/`: Custom management scripts for data processing

### Key Configuration Files
- `config/settings/base.py`: Core Django settings
- `config/settings/local.py`: Development-specific settings
- `pyproject.toml`: Tool configurations (pytest, black, isort, mypy)
- `setup.cfg`: flake8 and pycodestyle configuration
- `.pre-commit-config.yaml`: Pre-commit hooks configuration

### Database Architecture
- **PostgreSQL** with pgvector extension for vector similarity search
- **Redis** for caching and Celery message broker
- **Historical tracking** using django-simple-history for audit trails
- **Vector embeddings** for movie recommendations using OpenAI API

### API Architecture
- **Django REST Framework** for API endpoints
- **drf-spectacular** for OpenAPI documentation
- **Token authentication** and session authentication
- **CORS enabled** for cross-origin requests
- **django-ninja** for additional API endpoints (Discord service)

### Background Tasks
- **Celery** with Redis broker for async tasks
- **django-celery-beat** for scheduled tasks
- **Flower** for task monitoring (port 5555)

### External Integrations
- **OpenAI API** for embeddings and AI features
- **Discord API** for bot functionality
- **Instagram/TikTok APIs** for content monitoring
- **AWS S3** with boto3 for file storage
- **Telegram bots** for notifications

### Environment Configuration
- Uses **django-environ** for environment variable management
- Settings split across multiple files (base, local, production, test)
- **django-hosts** for multi-domain routing

### Security Features
- **django-allauth** for authentication
- **CORS headers** configuration
- **Health checks** for monitoring
- **Prometheus metrics** integration

## Common Patterns

### Custom Management Scripts
- Use `python manage.py runscript <script_name>` for custom data processing
- Scripts located in `scripts/` directory with `run()` function

### Model Patterns
- Historical tracking with `django-simple-history`
- Vector fields using pgvector for similarity search
- Custom model mixins in `models/base.py`

### API Patterns
- Pagination classes for list views
- Serializers with nested relationships
- ViewSets with custom actions

### Background Task Patterns
- Celery tasks in `tasks.py` files
- Batch processing for efficiency
- Error handling with fallback mechanisms

## Services Access

### Local Development URLs
- Django: http://localhost:8000
- Admin: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/api/schema/swagger-ui/
- Flower: http://localhost:5555
- Dozzle (Docker logs): http://localhost:9999

### Testing Strategy
- **pytest** with django integration
- **factory-boy** for test data generation
- **coverage** for test coverage reporting
- **django-coverage-plugin** for Django-specific coverage
