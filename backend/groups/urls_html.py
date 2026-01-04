from django.urls import path
from .views_html import GroupListView, GroupDetailView, CreateGroupView

urlpatterns = [
    path('', GroupListView.as_view(), name='groups-html'),
    path('create/', CreateGroupView.as_view(), name='create-group-html'),
    path('<int:pk>/', GroupDetailView.as_view(), name='group-detail-html'),
]
