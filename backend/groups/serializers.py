from rest_framework import serializers
from .models import StudyGroup, GroupMembership, GroupMessage, GroupResource, StudySession
from courses.serializers import CourseSerializer
from accounts.serializers import UserSerializer

class GroupMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = GroupMembership
        fields = ['id', 'user', 'role', 'joined_at', 'is_banned']
        read_only_fields = ['joined_at']


class StudyGroupSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    message_count = serializers.IntegerField(read_only=True)
    is_member = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    
    class Meta:
        model = StudyGroup
        fields = [
            'id', 'name', 'slug', 'description', 'course',
            'creator', 'privacy', 'max_members', 'is_active',
            'member_count', 'message_count', 'featured_image',
            'created_at', 'updated_at', 'is_member', 'can_join'
        ]
        read_only_fields = ['slug', 'creator', 'member_count', 'message_count', 'created_at', 'updated_at']
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False
    
    def get_can_join(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            can_join, message = obj.can_join(request.user)
            return {'can_join': can_join, 'message': message}
        return {'can_join': False, 'message': 'Login required'}


class GroupMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = GroupMessage
        fields = [
            'id', 'group', 'sender', 'content', 'is_system_message',
            'is_pinned', 'attachment', 'attachment_name', 'created_at'
        ]
        read_only_fields = ['sender', 'created_at']


class GroupResourceSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = GroupResource
        fields = [
            'id', 'group', 'name', 'description', 'file',
            'file_type', 'file_size', 'download_count',
            'uploaded_by', 'uploaded_at'
        ]
        read_only_fields = ['uploaded_by', 'download_count', 'uploaded_at']


class StudySessionSerializer(serializers.ModelSerializer):
    facilitator = UserSerializer(read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    
    class Meta:
        model = StudySession
        fields = [
            'id', 'group', 'group_name', 'title', 'description',
            'session_type', 'facilitator', 'start_time', 'end_time',
            'is_recurring', 'recurrence_pattern', 'meeting_link',
            'meeting_platform', 'max_participants', 'is_cancelled',
            'created_at'
        ]
        read_only_fields = ['facilitator', 'created_at']


class CreateStudyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyGroup
        fields = ['name', 'description', 'course', 'privacy', 'max_members', 'featured_image']
    
    def create(self, validated_data):
        request = self.context.get('request')
        group = StudyGroup.objects.create(
            creator=request.user,
            **validated_data
        )
        # Add creator as admin member
        GroupMembership.objects.create(
            user=request.user,
            group=group,
            role='admin'
        )
        group.member_count = 1
        group.save()
        return group
