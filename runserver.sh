#!/bin/sh

# Run migrations
echo "Running migrations..."
yes | python manage.py migrate

# Run tests
echo "Running tests..."
python manage.py test

# Check if tests were successful
if [ $? -eq 0 ]; then
  echo "Tests passed. Starting server..."
  gunicorn social_network.wsgi:application -b 0.0.0.0:8000 --reload --timeout=600
else
  echo "Tests failed. Server will not start."
  exit 1
fi