from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CourseSerializer
from .models import Course
from django.http import HttpResponse

# Create your views here.
"""
for testing

"""
def index(request):
    return HttpResponse("Hello, world")

#regualr django view not API for HTML page 
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/list.html', {'courses': courses})

#for API endpoint
@api_view(['GET'])
def course_list_api(request):
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

