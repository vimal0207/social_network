# SOCIAL NETWORK

This is a Django-based social network project that allows users to sign up, log in, send and manage friend requests, and search for users. The project uses PostgreSQL as the database and includes a Docker setup for easy deployment.

### Features
- User authentication (sign up, log in)
- User profile management
- Friend request system (send, accept, reject)
- User search functionality
- Token-based authentication using JWT

### Requirements
- Python
- Django
- Django REST Framework
- Django REST Framework Simplejwt
- Docker
- Docker Compose
- Gunicorn
- Psycopg2 Binary
  
### Project Structure
```
social_network/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env
├── manage.py
├── requirements.txt
├── social_network/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── user/
│   ├── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   ├── model_managers.py
│   ├── model_choices.py
│   ├── helper.py
│   ├── choices.py
└── scripts/
    ├── runserver.sh
```

### Setup Instructions
#### Prerequisites
- Docker
- Docker Compose

### Environment Variables
Create a .env file in the root directory and add the following variables:
```
SECRET_KEY=your_secret_key
ENVIRONMENT="LOCAL/DEV/STAGING/PRODUCTION"

ALLOWED_HOSTS="*"

POSTGRES_HOST=your_db_host
POSTGRES_PORT="5432"
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
```
> For creating a secret key, you can use [djecrety](https://djecrety.ir/).

### Docker Setup
- Build the Docker containers:
```
docker-compose up --build
```
- Run the project:
```
docker-compose up -d
``` 

### Accessing the Application
Once the containers are up and running, you can access the application at http://0.0.0.0:8000.

### API Documentation
The API endpoints can be tested using Postman. Import the following Postman collection to get started:

[Api Collection](api_postman_collection.json)
