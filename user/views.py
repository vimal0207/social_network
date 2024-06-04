from datetime import datetime, timedelta

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView

from django.db.models import Q
from django.db import transaction
from django.core.validators import EmailValidator

from base.views import BaseListView

from user.models import FriendRequest, UserData, User
from user.serializers import (UserSerializer, LoginSerializer, UserSearchSerializer, FriendRequestSerializer, 
                              ErrorSerializer, SelfFriendRequestSerializer)
from user.helper import generate_user_token, check_missing_fields


class SignupView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_classes = []

    @check_missing_fields("email", "password", "name")
    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email')
        name = data.get('name')

        email_validator = EmailValidator()
        try:
            email_validator(email)
        except Exception as _:
            return Response({'message': 'Invalid email format', 'error': 'invalid_email_format'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                if User.objects.filter(email=email).exists():
                    return Response({'message': 'Email already exists', 'error': 'email_exists'}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = self.serializer_class(data=data)
                if serializer.is_valid():
                    user = serializer.save()
                else:
                    return Response({'message': 'Something Went Wrong', 'errors': str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
                UserData.objects.create(user=user, name=name)
        except Exception as e:
            return Response({'message': 'Something Went Wrong', 'errors': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'User Created Successfully'}, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = []

    @check_missing_fields("email", "password")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
        else:
            error_serializer = ErrorSerializer(serializer.errors)
            return Response(error_serializer.data, status=status.HTTP_400_BAD_REQUEST)
        
        data = generate_user_token(user)
        data['user'] = UserSerializer(user).data
        return Response(data)


class CustomTokenRefreshView(TokenRefreshView):
    throttle_classes = []

    @check_missing_fields("refresh")
    def post(self, request):
        return super().post(request)
    

class UserSearchView(BaseListView):
    serializer_class = UserSearchSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return UserData.objects.select_related('user').filter(
            Q(user__email__iexact=query) |
            Q(name__icontains=query)
        ).exclude(user=self.request.user)


class FriendRequestView(BaseListView):
    serializer_class = FriendRequestSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SelfFriendRequestSerializer
        else:
            return FriendRequestSerializer
    
    def get_queryset(self):
        data = self.request.query_params
        status = data.get('status')
        return FriendRequest.objects.filter(
            to_user_id=self.request.user.id, status=status
        )
    
    @check_missing_fields("status")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


    @check_missing_fields("to_user_id")
    def post(self, request):
        to_user_id = self.request.data.get('to_user_id')
        from_user_id = self.request.user.id
        data = {"from_user_id" : from_user_id, "to_user_id" :to_user_id}

        missing_fields = []
        if not to_user_id:
            missing_fields.append('to_user_id')

        if missing_fields:
            return Response({
                'message': 'Missing required fields',
                'error': 'missing_fields',
                'missing_fields': missing_fields
            }, status=status.HTTP_400_BAD_REQUEST)

        if int(to_user_id) == int(from_user_id):
            return Response({'message': 'You cant send request to yourself', "error" : "circular error"}, status=status.HTTP_400_BAD_REQUEST)

        if not UserData.objects.filter(user_id=to_user_id).exists():
            return Response({'message': 'Invalid User Id', "error" : "invalid_id"}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(status='pending', **data).exists():
            return Response({'message': 'Friend request already sent', "error" : "request_in_pending_queue"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif FriendRequest.objects.filter(status='accepted', **data).exists():
            return Response({'message': 'Already In Friend List', "error" : "already_a_friend"}, status=status.HTTP_400_BAD_REQUEST)
        
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(from_user_id=from_user_id, created_at__gte=one_minute_ago)
        if recent_requests.count() >= 3:
            return Response({'message': 'You cannot send more than 3 friend requests in a minute', "error" : "limit_exceed"}, status=status.HTTP_400_BAD_REQUEST)

        serailizer = self.serializer_class(data={"from_user_id" : from_user_id, "to_user_id" :to_user_id})
        if serailizer.is_valid():
            serailizer.save()
        else:
            return Response({'message': 'Something Went Wrong', "error" : str(serailizer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Friend Request Sent Successfully'}, status=status.HTTP_201_CREATED)
    
    @check_missing_fields("action")
    def patch(self, request, pk, *args, **kwargs):
        user_id = request.user.id
        if not FriendRequest.objects.filter(to_user_id=user_id, status='pending', id=pk).exists():
            return Response({'message': 'No Request Found', "error" : "not_found"}, status=status.HTTP_400_BAD_REQUEST)
            
        instance = FriendRequest.objects.get(to_user_id=user_id, status='pending', id=pk)
        action = request.data.get('action')
        if action in ["accepted", "rejected"]:
            instance.status = action
        else:
            return Response({'message': 'Invalid action', "error" : "invalid_action"}, status=status.HTTP_400_BAD_REQUEST)
        instance.save()
        return Response({'message': 'Friend Request Accepted Successfully'})
    
    