from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
User = settings.AUTH_USER_MODEL

class Course(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all', 'All Levels'),
    )
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=200, blank=True)

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    
    # Course details
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    preview_video_url = models.URLField(blank=True, help_text="YouTube/Vimeo URL for preview")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    category = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    # Pricing
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    discount_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Stats
    estimated_hours = models.PositiveIntegerField(default=0, help_text="Total course duration in hours")
    total_lectures = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Ratings
    average_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from title"""
        if not self.slug:
            self.slug = slugify(self.title)
            # Make slug unique
            original_slug = self.slug
            counter = 1
            while Course.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    @property
    def current_price(self):
        """Get current price (discount if available)"""
        if self.discount_price and self.discount_price < (self.price or 0):
            return self.discount_price
        return self.price or 0
    
    @property
    def is_available(self):
        """Check if course is available for enrollment"""
        return self.status == 'published' and self.is_approved
    
    @property
    def tag_list(self):
        """Convert tags string to list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    def enroll_student(self, student):
        """Enroll a student in this course"""
        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            course=self,
            defaults={'enrolled_at': timezone.now()}
        )
        return enrollment, created
    
    def is_student_enrolled(self, student):
        """Check if student is enrolled"""
        if not student or not student.is_authenticated:
            return False
        return self.course_enrollments.filter(student=student).exists()
    
    def get_student_enrollment(self, student):
        """Get enrollment for a specific student"""
        try:
            return self.course_enrollments.get(student=student)
        except Enrollment.DoesNotExist:
            return None
    
class Video(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/')
    video_url = models.URLField(blank=True, help_text="External video URL (optional)")
    order = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Video duration in minutes")
    is_preview = models.BooleanField(default=False, help_text="Free preview for non-enrolled users")
    
    # Only ONE created_at field
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    """Track student enrollments in courses"""
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Progress tracking
    progress_percentage = models.FloatField(default=0.0)
    last_accessed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
    def save(self, *args, **kwargs):
        # Auto-update course student count
        if not self.pk:  # New enrollment
            super().save(*args, **kwargs)
            self.course.total_students = self.course.course_enrollments.count()
            self.course.save()
        else:
            super().save(*args, **kwargs)


class CourseProgress(models.Model):
    """Track progress through individual course lectures"""
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='progress'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='student_progress'
    )
    completed = models.BooleanField(default=False)
    watched_duration = models.IntegerField(default=0)  # Seconds watched
    total_duration = models.IntegerField(default=0)    # Video duration in seconds
    last_watched_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['enrollment', 'video']
    
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.video.title}"
