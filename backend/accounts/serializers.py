from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
#to translator between python object and JSON, validation for incoming data and normalizer for outgoing data

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User objects"""
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password',
            'first_name', 'last_name', 'role',
            'bio', 'profile_picture', 'phone',
            'website', 'location'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """Create and return a new user with encrypted password"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'student')
        )
        return user
    
    def update(self, instance, validated_data):
        """Update a user, setting the password correctly if provided"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication"""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )
    
    def validate(self, attrs):
        """Validate and authenticate the user"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )
        
        if not user:
            msg = 'Unable to authenticate with provided credentials'
            raise serializers.ValidationError(msg, code='authentication')
        
        attrs['user'] = user
        return attrs
