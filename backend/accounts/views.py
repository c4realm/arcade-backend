from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import logout
from .serializers import UserSerializer, AuthTokenSerializer
from django.views.generic import TemplateView


# Create your views here.
#creating a authentication views

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can register


class LoginView(ObtainAuthToken):
    """Login user and return auth token"""
    serializer_class = AuthTokenSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'profile_picture': user.profile_picture.url if user.profile_picture else None
        })


class LogoutView(APIView):
    """Logout user by deleting token"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Delete the token to logout
        request.user.auth_token.delete()
        logout(request)
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class LoginViewHTML(TemplateView):
    template_name = 'accounts/login.html'

class RegisterViewHTML(TemplateView):
    template_name = 'accounts/register.html'

class DashboardView(TemplateView):
    template_name = 'accounts/dashboard.html'
