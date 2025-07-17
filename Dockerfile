## Use Python 3.11 slim image
#FROM python:3.11-slim
#
## Set environment variables
#ENV PYTHONDONTWRITEBYTECODE=1 \
#    PYTHONUNBUFFERED=1 \
#    DJANGO_SETTINGS_MODULE=config.settings.prod
#
## Set work directory
#WORKDIR /app
#
## Install system dependencies
#RUN apt-get update \
#    && apt-get install -y --no-install-recommends \
#        build-essential \
#        libpq-dev \
#        curl \
#        netcat-traditional \
#        gettext \
#    && rm -rf /var/lib/apt/lists/*
#
## Install Python dependencies
#COPY requirements/prod.txt /app/requirements/
#RUN pip install --no-cache-dir -r requirements/prod.txt
#
## Copy project
#COPY . /app/
#
## Create non-root user
#RUN adduser --disabled-password --gecos '' appuser
#
## Change ownership of the app directory to the app user
#RUN chown -R appuser:appuser /app
#USER appuser
#
## Collect static files
#RUN python manage.py collectstatic --noinput
#
## Expose port
#EXPOSE 8000
#
## Health check
#HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#    CMD curl -f http://localhost:8000/health/ || exit 1
#
## Run the application
#CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

FROM python:3.11-slim

# Working directory
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create SQLite directory (development uchun)
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]