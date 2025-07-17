# OneSport - Professional HR/Recruiting Platform

[![CI/CD Pipeline](https://github.com/username/onesport/workflows/OneSport%20CI/CD%20Pipeline/badge.svg)](https://github.com/username/onesport/actions)
[![Coverage](https://codecov.io/gh/username/onesport/branch/main/graph/badge.svg)](https://codecov.io/gh/username/onesport)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-4.2-green.svg)](https://www.djangoproject.com/)

OneSport is a comprehensive HR/Recruiting platform that connects companies with top recruiters and candidates. Built with Django REST Framework, it provides a scalable, secure, and feature-rich solution for modern recruitment needs.

## 🚀 Features

### 🏢 **For Companies (Clients)**
- **Job Management**: Create, edit, and manage job postings with detailed requirements
- **Recruiter Network**: Access to verified recruiters and agencies
- **Application Tracking**: Monitor recruiter applications and candidate pipelines
- **Real-time Chat**: Direct communication with recruiters
- **Performance Analytics**: Track hiring metrics and recruiter performance
- **Team Collaboration**: Multi-user support with role-based permissions

### 🎯 **For Recruiters**
- **Job Discovery**: Browse and apply to relevant job opportunities
- **Portfolio Management**: Showcase expertise and track record
- **Client Communication**: Direct messaging with hiring managers
- **Candidate Management**: Track and manage candidate applications
- **Commission Tracking**: Monitor earnings and payment history
- **Agency Support**: Multi-recruiter agency management

### 🔧 **Technical Features**
- **RESTful API**: Comprehensive API with Swagger documentation
- **Real-time Messaging**: WebSocket-powered chat system
- **File Management**: Secure document upload and storage
- **Search & Filtering**: Advanced search capabilities
- **Authentication**: JWT-based security with role management
- **Scalable Architecture**: Docker containerization and microservices ready

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Database      │
│   (React/Vue)   │◄──►│   (Django)      │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │   Redis Cache   │    │   File Storage  │
                    │   (Sessions)    │    │   (Media Files) │
                    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │   Celery        │    │   WebSocket     │
                    │   (Background)  │    │   (Real-time)   │
                    └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Task Queue**: Celery + Redis
- **Real-time**: Django Channels + WebSocket
- **Authentication**: JWT (SimpleJWT)
- **API Docs**: drf-yasg (Swagger/OpenAPI)
- **File Storage**: Django FileSystemStorage
- **Email**: Mailgun integration
- **Deployment**: Docker + Docker Compose

## 📋 Requirements

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (for frontend)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/username/onesport.git
cd onesport
```

### 2. Environment Setup

```bash
# Copy environment file
cp .env.example .env

# Edit environment variables
nano .env
```

### 3. Docker Setup (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load initial data
docker-compose exec web python manage.py loaddata fixtures/initial_data.json
```

### 4. Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# Setup database
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata fixtures/initial_data.json

# Run development server
python manage.py runserver
```

## 🧪 Testing

### Run All Tests

```bash
# Using test runner script
python run_tests.py

# With coverage
python run_tests.py --coverage

# Specific apps
python run_tests.py grid.users grid.jobs

# Parallel execution
python run_tests.py --parallel
```

### Code Quality Checks

```bash
# Run all quality checks
python run_tests.py --all-checks

# Individual checks
python run_tests.py --lint
python run_tests.py --type-check
python run_tests.py --security

# Format code
python run_tests.py --format
```

### Using Django's Test Runner

```bash
# Run all tests
python manage.py test

# Specific app
python manage.py test grid.users

# With coverage
coverage run --source='.' manage.py test
coverage report -m
coverage html
```

## 📊 Database Management

### Backup Database

```bash
# Create backup
python manage_db.py backup create --name "my_backup"

# List backups
python manage_db.py backup list

# Restore backup
python manage_db.py backup restore backups/my_backup.sql
```

### Migration Management

```bash
# Safe migration with backup
python manage_db.py migrate safe

# Check migration conflicts
python manage_db.py migrate check

# Rollback migration
python manage_db.py migrate rollback grid.users 0001
```

### Deployment

```bash
# Full deployment with checks
python manage_db.py deploy run

# Pre-deployment checks only
python manage_db.py deploy check

# Rollback deployment
python manage_db.py deploy rollback backup_name
```

## 🔧 API Documentation

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs/
- **ReDoc**: http://localhost:8000/redoc/
- **JSON Schema**: http://localhost:8000/swagger.json

### API Authentication

```bash
# Get access token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in requests
curl -X GET http://localhost:8000/api/jobs/ \
  -H "Authorization: Bearer <access_token>"
```

### Example API Calls

```bash
# List jobs
curl -X GET "http://localhost:8000/api/jobs/?search=engineer" \
  -H "Authorization: Bearer <token>"

# Create job
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Developer",
    "salary_min": 80000,
    "job_type": 1,
    "client": 1
  }'

# Upload job attachment
curl -X POST http://localhost:8000/api/job-attachments/ \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "job=1"
```

## 🌐 Frontend Integration

See [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) for detailed frontend integration guide including:

- React/Vue.js setup
- Authentication flow
- API client configuration
- WebSocket integration
- File upload handling
- Error handling
- Performance optimization

## 📁 Project Structure

```
OneSport/
├── 📁 config/                 # Django configuration
│   ├── settings/              # Environment-specific settings
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py               # WSGI configuration
├── 📁 grid/                   # Main application package
│   ├── 📁 users/             # User management
│   ├── 📁 clients/           # Client/company management
│   ├── 📁 jobs/              # Job posting management
│   ├── 📁 recruiters/        # Recruiter management
│   ├── 📁 chats/             # Real-time messaging
│   ├── 📁 hires/             # Hiring process management
│   ├── 📁 candidates/        # Candidate management
│   ├── 📁 core/              # Core utilities
│   └── 📁 site_settings/     # Application settings
├── 📁 requirements/           # Python dependencies
├── 📁 fixtures/              # Initial data
├── 📁 nginx/                 # Nginx configuration
├── 📄 docker-compose.yml     # Docker services
├── 📄 Dockerfile            # Docker image
├── 📄 manage_db.py          # Database management
├── 📄 run_tests.py          # Test runner
└── 📄 README.md             # This file
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-based Access**: CLIENT, RECRUITER, ADMIN roles
- **Permission System**: Granular permissions per endpoint
- **CORS Protection**: Configurable cross-origin settings
- **Rate Limiting**: API rate limiting via nginx
- **File Validation**: Secure file upload with type checking
- **SQL Injection Protection**: Django ORM protection
- **XSS Protection**: Built-in Django security middleware

## 🚀 Deployment

### Docker Deployment

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f web

# Scale services
docker-compose up -d --scale web=3
```

### Manual Deployment

```bash
# Install production dependencies
pip install -r requirements/prod.txt

# Collect static files
python manage.py collectstatic --noinput

# Run with gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Environment Variables

Create `.env` file with:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_SETTINGS_MODULE=config.settings.prod
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=onesport_prod
DB_USER=onesport_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379

# Email
MAILGUN_API_KEY=your-mailgun-key
MAILGUN_SENDER_DOMAIN=yourdomain.com

# External APIs
PROXYCURL_API_KEY=your-proxycurl-key

# Social Auth
GRID_API_SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-google-key
GRID_API_SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-google-secret

# URLs
API_BASE_URL=https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com
```

## 📈 Monitoring & Logging

### Health Checks

```bash
# Application health
curl http://localhost:8000/health/

# Database status
python manage.py dbshell -c "SELECT 1;"

# Redis status
redis-cli ping
```

### Logging

Logs are configured for different environments:

- **Development**: Console output with DEBUG level
- **Production**: File-based logging with structured format
- **Docker**: Container logs via docker-compose logs

### Monitoring Services

- **Flower**: Celery task monitoring at http://localhost:5555
- **Django Admin**: Admin interface at /admin/
- **API Docs**: Interactive API docs at /docs/

## 🤝 Contributing

### Development Setup

```bash
# Install pre-commit hooks
pre-commit install

# Run tests before committing
python run_tests.py --all-checks

# Format code
python run_tests.py --format
```

### Code Style

- **Python**: Follow PEP 8, use Black for formatting
- **Import Sorting**: Use isort with Black profile
- **Type Hints**: Use mypy for type checking
- **Documentation**: Docstrings for all public methods
- **Testing**: Maintain 80%+ test coverage

### Pull Request Process

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Write tests for new functionality
4. Ensure all tests pass
5. Run code quality checks
6. Commit changes (`git commit -m 'Add AmazingFeature'`)
7. Push to branch (`git push origin feature/AmazingFeature`)
8. Open Pull Request

## 📝 API Endpoints

### Authentication
- `POST /api/auth/registration/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `GET /api/auth/user/` - Get current user
- `PATCH /api/auth/user/` - Update user profile

### Jobs
- `GET /api/jobs/` - List jobs
- `POST /api/jobs/` - Create job
- `GET /api/jobs/{id}/` - Get job details
- `PATCH /api/jobs/{id}/` - Update job
- `DELETE /api/jobs/{id}/` - Delete job

### Clients
- `GET /api/clients/` - List clients
- `POST /api/clients/` - Create client
- `GET /api/clients/{id}/` - Get client details
- `PATCH /api/clients/{id}/` - Update client

### Recruiters
- `GET /api/recruiters/` - List recruiters
- `POST /api/recruiters/` - Create recruiter
- `GET /api/recruiters/{id}/` - Get recruiter details
- `PATCH /api/recruiters/{id}/` - Update recruiter

### Chat
- `GET /api/chats/rooms/` - List chat rooms
- `POST /api/chats/rooms/` - Create chat room
- `GET /api/chats/rooms/{id}/messages/` - Get messages
- `POST /api/chats/rooms/{id}/messages/` - Send message

## 🔧 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Reset database
python manage.py flush
python manage.py migrate
```

**Redis Connection Error**
```bash
# Check Redis status
redis-cli ping

# Restart Redis
sudo systemctl restart redis
```

**Docker Issues**
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# View container logs
docker-compose logs web
```

**Test Failures**
```bash
# Run with verbose output
python manage.py test --verbosity=2

# Run specific test
python manage.py test grid.users.tests.UserModelTests.test_create_user
```

## 📚 Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **DRF Documentation**: https://www.django-rest-framework.org/
- **Django Channels**: https://channels.readthedocs.io/
- **Celery Documentation**: https://docs.celeryproject.org/
- **Docker Documentation**: https://docs.docker.com/

## 📞 Support

- **Documentation**: [API Documentation](API_DOCUMENTATION.md)
- **Frontend Guide**: [Frontend Integration](FRONTEND_INTEGRATION.md)
- **Issues**: [GitHub Issues](https://github.com/username/onesport/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/onesport/discussions)
- **Email**: support@onesport.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django and DRF communities
- PostgreSQL development team
- Redis team
- All contributors and testers

---

**OneSport** - Connecting talent with opportunity through technology 🚀