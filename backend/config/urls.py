"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from courses.views import (
    HomeView, 
    course_list_html, 
    course_detail_html, 
    create_course_html
)
from accounts.views import (
    LoginViewHTML, 
    RegisterViewHTML, 
    DashboardView
)

urlpatterns = [
        #the admin

    path('admin/', admin.site.urls),
        #the api endpoints

    path('api/v1/', include('courses.urls')),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/', include('groups.urls')),

     # HTML pages Views
    path('', HomeView.as_view(), name='home'),
    path('courses/', course_list_html, name='courses-html'),
    path('courses/create/', create_course_html, name='create-course-html'),
    path('courses/<int:pk>/', course_detail_html, name='course-detail-html'),
    path('login/', LoginViewHTML.as_view(), name='login-html'),
    path('register/', RegisterViewHTML.as_view(), name='register-html'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]


# For serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

