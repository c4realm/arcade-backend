from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view(['GET'])
def course_list_api(request):
    return Response({
        'message': 'API is working!',
        'endpoint': '/api/v1/courses/',
        'next_steps': 'We will add real course data next'
    })


