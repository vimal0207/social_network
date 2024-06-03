from functools import wraps

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status

def generate_user_token(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }


def check_missing_fields(*required_fields):
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            req_method = request.method
            data = request.query_params if req_method == "GET" else request.data
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return Response({
                    'message': 'Missing required fields',
                    'error': 'missing_fields',
                    'missing_fields': missing_fields,
                    'required_fields': required_fields
                }, status=status.HTTP_400_BAD_REQUEST)
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator