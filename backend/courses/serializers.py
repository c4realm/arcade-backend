# backend/courses/serializers.py
from rest_framework import serializers
from .models import Course, Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'video_file', 'order', 'uploaded_at']

class CourseSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'creator', 'creator_name',
            'is_paid', 'price', 'is_approved', 'created_at', 'videos'
        ]
        read_only_fields = ['creator']  # Auto-set from request.user
