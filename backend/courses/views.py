# backend/courses/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Course
from .serializers import CourseSerializer
#this API end point get data from Database, convert to JSON format, send to fronted
@api_view(['GET'])
def course_list_api(request):
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

