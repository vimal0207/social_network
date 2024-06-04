from rest_framework import serializers
from user.models import User, FriendRequest, UserData


class ErrorSerializer(serializers.Serializer):
    def to_representation(self, instance):
        error_message = {}
        for field, errors in instance.items():
            if isinstance(errors, list) and len(errors) > 0:
                error_message[field] = errors[0]
            else:
                error_message[field] = errors
        return error_message
    

class UserSerializer(serializers.ModelSerializer):

    name = serializers.CharField(source='user_data.name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'].lower(),
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email').lower()
        password = data.get('password')
        
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'message' : 'Invalid Email', 'error' : 'invalid_email'})
        
        user = User.objects.get(email=email)

        if not user.check_password(password):
            raise serializers.ValidationError({'message' : 'Invalid Password', 'error' : 'invalid_password'})


        if not user.is_active:
            raise serializers.ValidationError({'message' : 'In Active Account', 'error' : 'inactive_user'})

        return user        
    

class UserSearchSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email')
    id = serializers.CharField(source='user_id')
    
    class Meta:
        model = UserData
        fields = ['id', 'email', 'name']


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSearchSerializer(read_only=True)
    to_user = UserSearchSerializer(read_only=True)
    from_user_id = serializers.IntegerField(write_only=False)
    to_user_id = serializers.IntegerField(write_only=False)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at', 'updated_at', 'to_user_id', 'from_user_id']

class SelfFriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSearchSerializer(read_only=True)
    from_user_id = serializers.IntegerField(write_only=False)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'status', 'created_at', 'updated_at', 'from_user_id']
        