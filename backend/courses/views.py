from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

from .models import Course
from .serializers import CourseSerializer, CourseCreateSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Video
from .serializers import VideoSerializer

# API Views
class CourseListView(generics.ListCreateAPIView):
    """List all courses or create new course"""
    queryset = Course.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateSerializer
        return CourseSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a course"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


@api_view(['GET'])
def course_list_api(request):
    """Legacy API endpoint"""
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


# HTML Views
class HomeView(TemplateView):
    template_name = 'home.html'


def course_list_html(request):
    """HTML view for course listing"""
    courses = Course.objects.all()
    return render(request, 'courses/list.html', {'courses': courses})


def course_detail_html(request, pk):
    """HTML view for single course"""
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'courses/detail.html', {'course': course})


def create_course_html(request):
    """HTML view for creating a course"""
    return render(request, 'courses/create.html')

class VideoListView(APIView):
    def get(self, request, course_id):
        videos = Video.objects.filter(course_id=course_id)
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)

