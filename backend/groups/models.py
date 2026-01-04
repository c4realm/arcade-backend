from django.db import models
from django.conf import settings
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL

class StudyGroup(models.Model):
    PRIVACY_CHOICES = (
        ('public', 'Public - Anyone can join'),
        ('private', 'Private - Invite only'),
        ('course', 'Course-based - For enrolled students only'),
    )
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='study_groups'
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_study_groups'
    )
    members = models.ManyToManyField(
        User,
        related_name='study_groups',
        through='GroupMembership'
    )
    
    # Group settings
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public')
    max_members = models.PositiveIntegerField(default=50)
    is_active = models.BooleanField(default=True)
    
    # Stats
    member_count = models.PositiveIntegerField(default=0)
    message_count = models.PositiveIntegerField(default=0)
    
    # Resources
    featured_image = models.ImageField(upload_to='study_groups/', null=True, blank=True)
    resources_folder = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug', 'privacy']),
            models.Index(fields=['course', 'created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name"""
        if not self.slug:
            self.slug = slugify(self.name)
            # Make slug unique
            original_slug = self.slug
            counter = 1
            while StudyGroup.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    @property
    def is_full(self):
        return self.member_count >= self.max_members
    
    def can_join(self, user):
        """Check if user can join this group"""
        if not self.is_active:
            return False, "Group is not active"
        
        if self.is_full:
            return False, "Group is full"
        
        if self.privacy == 'course' and self.course:
            # Check if user is enrolled in the course
            from courses.models import Enrollment
            if not Enrollment.objects.filter(student=user, course=self.course).exists():
                return False, "You must be enrolled in the course to join"
        
        if self.members.filter(id=user.id).exists():
            return False, "You are already a member"
        
        return True, "Can join"


class GroupMembership(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_banned = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'group']
    
    def __str__(self):
        return f"{self.user.username} in {self.group.name}"


class GroupMessage(models.Model):
    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='group_messages'
    )
    content = models.TextField()
    
    # Message types
    is_system_message = models.BooleanField(default=False)  # For joins/leaves
    is_pinned = models.BooleanField(default=False)
    
    # Resources
    attachment = models.FileField(upload_to='group_chat/', null=True, blank=True)
    attachment_name = models.CharField(max_length=200, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['group', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class GroupResource(models.Model):
    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='group_resources/')
    file_type = models.CharField(max_length=50, blank=True)
    file_size = models.PositiveIntegerField(default=0)  # In bytes
    download_count = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.name


class StudySession(models.Model):
    SESSION_TYPES = (
        ('lecture', 'Lecture Review'),
        ('qa', 'Q&A Session'),
        ('project', 'Project Work'),
        ('exam', 'Exam Preparation'),
    )
    
    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name='study_sessions'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='lecture')
    facilitator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='facilitated_sessions')
    
    # Scheduling
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=100, blank=True)
    
    # Virtual meeting
    meeting_link = models.URLField(blank=True)
    meeting_platform = models.CharField(max_length=50, blank=True)
    
    # Attendance
    max_participants = models.PositiveIntegerField(default=0)
    participants = models.ManyToManyField(User, through='SessionAttendance')
    
    # Status
    is_cancelled = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.title} - {self.group.name}"


class SessionAttendance(models.Model):
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['session', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.session.title}"
