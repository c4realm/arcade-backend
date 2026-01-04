from rest_framework import serializers
from .models import Course, Video

class VideoSerializer(serializers.ModelSerializer):
    duration_formatted = serializers.CharField(read_only=True)
    file_size_formatted = serializers.CharField(read_only=True)
    
    class Meta:
        model = Video
        fields = [
            'id', 'course', 'title', 'description',
            'video_file', 'video_url', 'thumbnail',
            'duration_seconds', 'duration_formatted',
            'file_size', 'file_size_formatted',
            'order', 'is_preview', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['course', 'file_size', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Calculate file size if video file is uploaded
        video_file = validated_data.get('video_file')
        if video_file:
            validated_data['file_size'] = video_file.size
        
        return super().create(validated_data)
class CourseSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'creator', 'creator_name',
            'is_paid', 'price', 'is_approved', 'created_at',
            'short_description', 'level', 'category', 'tags', 'status', 'videos'
        ]
        read_only_fields = ['creator']

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'description', 'is_paid', 'price']
