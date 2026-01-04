from django.urls import path
from . import views

urlpatterns = [
    # Study Groups
    path('groups/', views.StudyGroupListView.as_view(), name='studygroup-list'),
    path('groups/me/', views.MyStudyGroupsView.as_view(), name='my-studygroups'),
    path('groups/<int:pk>/', views.StudyGroupDetailView.as_view(), name='studygroup-detail'),
    path('groups/<int:pk>/join/', views.JoinStudyGroupView.as_view(), name='join-studygroup'),
    path('groups/<int:pk>/leave/', views.LeaveStudyGroupView.as_view(), name='leave-studygroup'),
    
    # Group Chat
    path('groups/<int:group_id>/messages/', views.GroupMessageListView.as_view(), name='group-messages'),
    
    # Group Resources
    path('groups/<int:group_id>/resources/', views.GroupResourceListView.as_view(), name='group-resources'),
    
    # Study Sessions
    path('groups/<int:group_id>/sessions/', views.StudySessionListView.as_view(), name='study-sessions'),
    
    # Legacy endpoint
    path('groups/legacy/', views.group_list_api, name='group-list-legacy'),
]
