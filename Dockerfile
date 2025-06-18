# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (for SQLite)
RUN apt-get update && apt-get install -y \
    netcat-openbsd gcc libsqlite3-dev --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run the app using Gunicorn with the correct wsgi module
CMD ["gunicorn", "carrie_search.wsgi:application", "--bind", "0.0.0.0:8000"]
