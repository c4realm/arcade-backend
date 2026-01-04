from django.db import models
from django.conf import settings
from django.utils.text import slugify

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
