from django.urls import path, include
from .views import course_list, course_list_api
from django.contrib import admin


urlpatterns = [
    path('', course_list, name='course_list'),
    path('api/courses/', course_list_api, name='course_list_api'),
    path('courses/', course_list_api, name='course_list_api'),
]

