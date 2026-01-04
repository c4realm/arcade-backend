from django.urls import path
from .views import CourseListView, CourseDetailView, course_list_api

urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    
]
