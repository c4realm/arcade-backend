from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from courses import views

# Import views
from courses.views import (
    HomeView, 
    course_list_html, 
    course_detail_html, 
    create_course_html
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/v1/', include('courses.urls')),
    path('api/v1/auth/', include('accounts.urls')),
    
    # HTML Pages
    path('', HomeView.as_view(), name='home'),
    path('courses/', course_list_html, name='courses-html'),
    path('courses/create/', create_course_html, name='create-course-html'),
    path('courses/<int:pk>/', course_detail_html, name='course-detail-html'),
    
    # Simple pages (we'll build these later)
    path('login/', TemplateView.as_view(template_name='accounts/login.html'), name='login-html'),
    path('register/', TemplateView.as_view(template_name='accounts/register.html'), name='register-html'),
    path('dashboard/', TemplateView.as_view(template_name='accounts/dashboard.html'), name='dashboard'),

    #path('courses/<int:pk>/upload-video/', views.video_upload_html, name='video-upload-html'),
]

# For serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
