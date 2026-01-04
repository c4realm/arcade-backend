from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
#extending the user model for learning platform

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student'
    )

    def __str__(self):
        return self.username
#for the profile fields
# bio for user descriptions
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)


     # Platform-specific fields, trust system for instructors

    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

# Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
# Methods
    def is_instructor(self):
        return self.role == 'instructor'
    
    def is_student(self):
        return self.role == 'student'
    
    def get_full_name_or_username(self):
        """Return full name if available, otherwise username"""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        ordering = ['-date_joined'] 
