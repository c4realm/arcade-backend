from django.urls import path
from .views import course_list_api


urlpatterns = [
      path('courses/', course_list_api, name='course_list_api'), 
]

