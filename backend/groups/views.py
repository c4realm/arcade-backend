from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.views.generic import TemplateView
from .models import StudyGroup

# Create your views here.

from .models import StudyGroup, GroupMembership, GroupMessage, GroupResource, StudySession
from .serializers import (
    StudyGroupSerializer, CreateStudyGroupSerializer,
    GroupMessageSerializer, GroupResourceSerializer,
    StudySessionSerializer, GroupMembershipSerializer
)

# Custom Permissions
class IsGroupMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, StudyGroup):
            return obj.members.filter(id=request.user.id).exists()
        return obj.group.members.filter(id=request.user.id).exists()

class IsGroupAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, StudyGroup):
            return GroupMembership.objects.filter(
                user=request.user, 
                group=obj, 
                role__in=['admin', 'moderator']
            ).exists()
        return GroupMembership.objects.filter(
            user=request.user, 
            group=obj.group, 
            role__in=['admin', 'moderator']
        ).exists()


# Study Group Views
class StudyGroupListView(generics.ListCreateAPIView):
    """List all study groups or create new group"""
    queryset = StudyGroup.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateStudyGroupSerializer
        return StudyGroupSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        queryset = StudyGroup.objects.filter(is_active=True)
        
        # Filter by course
        course_id = self.request.query_params.get('course', None)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Filter by privacy
        privacy = self.request.query_params.get('privacy', None)
        if privacy:
            queryset = queryset.filter(privacy=privacy)
        
        # Filter by search query
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')


class StudyGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a study group"""
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsGroupAdmin()]
        return [permissions.AllowAny()]


class JoinStudyGroupView(APIView):
    """Join a study group"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        group = get_object_or_404(StudyGroup, pk=pk)
        
        # Check if user can join
        can_join, message = group.can_join(request.user)
        if not can_join:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create membership
        membership, created = GroupMembership.objects.get_or_create(
            user=request.user,
            group=group,
            defaults={'role': 'member'}
        )
        
        if created:
            # Update member count
            group.member_count += 1
            group.save()
            
            # Create system message
            GroupMessage.objects.create(
                group=group,
                sender=request.user,
                content=f"{request.user.username} joined the group",
                is_system_message=True
            )
            
            return Response({'message': 'Successfully joined the group'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Already a member'}, status=status.HTTP_400_BAD_REQUEST)


class LeaveStudyGroupView(APIView):
    """Leave a study group"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        group = get_object_or_404(StudyGroup, pk=pk)
        
        try:
            membership = GroupMembership.objects.get(user=request.user, group=group)
            
            # Check if user is the last admin
            if membership.role == 'admin':
                admin_count = GroupMembership.objects.filter(group=group, role='admin').count()
                if admin_count <= 1:
                    return Response(
                        {'error': 'Cannot leave as the only admin. Transfer admin role first.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            membership.delete()
            
            # Update member count
            group.member_count -= 1
            group.save()
            
            # Create system message
            GroupMessage.objects.create(
                group=group,
                sender=request.user,
                content=f"{request.user.username} left the group",
                is_system_message=True
            )
            
            return Response({'message': 'Successfully left the group'})
            
        except GroupMembership.DoesNotExist:
            return Response({'error': 'Not a member of this group'}, status=status.HTTP_400_BAD_REQUEST)


# Group Chat Views
class GroupMessageListView(generics.ListCreateAPIView):
    """List messages in a group or post new message"""
    serializer_class = GroupMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupMember]
    
    def get_queryset(self):
        group = get_object_or_404(StudyGroup, pk=self.kwargs['group_id'])
        return GroupMessage.objects.filter(group=group).order_by('-created_at')[:50]
    
    def perform_create(self, serializer):
        group = get_object_or_404(StudyGroup, pk=self.kwargs['group_id'])
        serializer.save(group=group, sender=self.request.user)
        
        # Update message count
        group.message_count += 1
        group.save()


# Group Resources Views
class GroupResourceListView(generics.ListCreateAPIView):
    """List or upload resources in a group"""
    serializer_class = GroupResourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupMember]
    
    def get_queryset(self):
        group = get_object_or_404(StudyGroup, pk=self.kwargs['group_id'])
        return GroupResource.objects.filter(group=group).order_by('-uploaded_at')
    
    def perform_create(self, serializer):
        group = get_object_or_404(StudyGroup, pk=self.kwargs['group_id'])
        
        # Get file info
        file = self.request.FILES.get('file')
        if file:
            serializer.validated_data['file_size'] = file.size
            serializer.validated_data['file_type'] = file.content_type
        
        serializer.save(group=group, uploaded_by=self.request.user)


# Study Session Views
class StudySessionListView(generics.ListCreateAPIView):
    """List or create study sessions"""
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsGroupMember]
    
    def get_queryset(self):
        group = get_object_or_404(StudyGroup, pk=self.kwargs['group_id'])
        now = timezone.now()
        return StudySession.objects.filter(
            group=group,
            start_time__gte=now,
            is_cancelled=False
        ).order_by('start_time')
    
    def perform_create(self, serializer):
        group = get_object_or_404(StudyGroup, pk=self.kwargs['group_id'])
        serializer.save(group=group, facilitator=self.request.user)


class MyStudyGroupsView(generics.ListAPIView):
    """Get study groups where user is a member"""
    serializer_class = StudyGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return StudyGroup.objects.filter(members=user, is_active=True).order_by('-created_at')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def group_list_api(request):
    """Legacy API endpoint"""
    groups = StudyGroup.objects.filter(is_active=True)
    serializer = StudyGroupSerializer(groups, many=True, context={'request': request})
    return Response(serializer.data)

class GroupListView(TemplateView):
    template_name = 'groups/list.html'

class GroupDetailView(TemplateView):
    template_name = 'groups/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = get_object_or_404(StudyGroup, pk=kwargs['pk'])
        context['group'] = group
        return context

class CreateGroupView(TemplateView):
    template_name = 'groups/create.html'

