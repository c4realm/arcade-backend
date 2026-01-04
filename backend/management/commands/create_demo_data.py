# backend/management/commands/create_demo_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course, Video
from groups.models import StudyGroup
import random
from faker import Faker

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Create demo data for presentation'
    
    def handle(self, *args, **kwargs):
        self.stdout.write("🎬 Creating demo data for Arcade presentation...")
        
        # Create demo users
        users = self.create_demo_users()
        
        # Create demo courses
        courses = self.create_demo_courses(users['instructors'])
        
        # Create demo videos
        self.create_demo_videos(courses, users['instructors'])
        
        # Create demo study groups
        self.create_demo_groups(courses, users['instructors'], users['students'])
        
        self.stdout.write(self.style.SUCCESS("✅ Demo data created successfully!"))
        self.stdout.write("\n📊 DEMO ACCOUNTS:")
        self.stdout.write("👑 Admin: admin / admin123")
        self.stdout.write("👨‍🏫 Instructor: instructor1 / test123")
        self.stdout.write("👨‍🎓 Student: student1 / test123")
        self.stdout.write("\n🌐 Access the site at: http://127.0.0.1:8000/")
    
    def create_demo_users(self):
        self.stdout.write("👥 Creating demo users...")
        
        # Create admin if not exists
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@arcade.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        
        # Create demo instructors
        instructors = []
        for i in range(3):
            instructor, created = User.objects.get_or_create(
                username=f'instructor{i+1}',
                defaults={
                    'email': f'instructor{i+1}@arcade.com',
                    'role': 'instructor',
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'bio': fake.text(max_nb_chars=200)
                }
            )
            if created:
                instructor.set_password('test123')
                instructor.save()
            instructors.append(instructor)
        
        # Create demo students
        students = []
        for i in range(5):
            student, created = User.objects.get_or_create(
                username=f'student{i+1}',
                defaults={
                    'email': f'student{i+1}@arcade.com',
                    'role': 'student',
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'bio': fake.text(max_nb_chars=150)
                }
            )
            if created:
                student.set_password('test123')
                student.save()
            students.append(student)
        
        return {'admin': admin, 'instructors': instructors, 'students': students}
    
    def create_demo_courses(self, instructors):
        self.stdout.write("📚 Creating demo courses...")
        
        course_templates = [
            {
                'title': 'Python Programming for Beginners',
                'description': 'Learn Python from scratch with hands-on projects. Perfect for absolute beginners.',
                'category': 'Programming',
                'level': 'beginner',
                'is_paid': False,
                'estimated_hours': 12,
                'tags': 'python, programming, beginners'
            },
            {
                'title': 'Web Development with Django',
                'description': 'Build full-stack web applications using Django and React.',
                'category': 'Web Development',
                'level': 'intermediate',
                'is_paid': True,
                'price': 49.99,
                'estimated_hours': 20,
                'tags': 'django, python, web, react'
            },
            {
                'title': 'Data Science Fundamentals',
                'description': 'Master data analysis, visualization, and machine learning basics.',
                'category': 'Data Science',
                'level': 'intermediate',
                'is_paid': True,
                'price': 79.99,
                'estimated_hours': 15,
                'tags': 'data, python, machine-learning, analysis'
            },
            {
                'title': 'UI/UX Design Principles',
                'description': 'Learn to create beautiful and user-friendly interfaces.',
                'category': 'Design',
                'level': 'beginner',
                'is_paid': False,
                'estimated_hours': 8,
                'tags': 'design, ui, ux, figma'
            },
            {
                'title': 'JavaScript Masterclass',
                'description': 'From basics to advanced concepts, master modern JavaScript.',
                'category': 'Programming',
                'level': 'advanced',
                'is_paid': True,
                'price': 89.99,
                'estimated_hours': 25,
                'tags': 'javascript, web, frontend, es6'
            }
        ]
        
        courses = []
        for i, template in enumerate(course_templates):
            course, created = Course.objects.get_or_create(
                title=template['title'],
                defaults={
                    'description': template['description'],
                    'creator': instructors[i % len(instructors)],
                    'category': template['category'],
                    'level': template['level'],
                    'is_paid': template['is_paid'],
                    'price': template.get('price'),
                    'estimated_hours': template['estimated_hours'],
                    'tags': template['tags'],
                    'status': 'published',
                    'is_approved': True,
                    'is_featured': i < 2,  # First 2 courses are featured
                    'total_students': random.randint(50, 200),
                    'average_rating': round(random.uniform(4.0, 5.0), 1),
                    'rating_count': random.randint(20, 100)
                }
            )
            if created:
                courses.append(course)
        
        return courses
    
    def create_demo_videos(self, courses, instructors):
        self.stdout.write("🎥 Creating demo videos...")
        
        video_templates = [
            {'title': 'Introduction', 'duration': 300, 'order': 1, 'is_preview': True},
            {'title': 'Getting Started', 'duration': 600, 'order': 2, 'is_preview': True},
            {'title': 'Core Concepts', 'duration': 900, 'order': 3, 'is_preview': False},
            {'title': 'Hands-on Practice', 'duration': 1200, 'order': 4, 'is_preview': False},
            {'title': 'Advanced Topics', 'duration': 1500, 'order': 5, 'is_preview': False},
            {'title': 'Project Building', 'duration': 1800, 'order': 6, 'is_preview': False},
            {'title': 'Conclusion', 'duration': 300, 'order': 7, 'is_preview': True},
        ]
        
        for course in courses:
            for i, template in enumerate(video_templates):
                video, created = Video.objects.get_or_create(
                    course=course,
                    title=f"{course.title}: {template['title']}",
                    defaults={
                        'description': f"This video covers {template['title'].lower()} for {course.title}.",
                        'video_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
                        'duration_seconds': template['duration'],
                        'order': template['order'],
                        'is_preview': template['is_preview'],
                        'is_published': True
                    }
                )
            
            # Update course video count
            course.total_lectures = course.videos.count()
            course.save()
    
    def create_demo_groups(self, courses, instructors, students):
        self.stdout.write("👥 Creating demo study groups...")
        
        group_templates = [
            {'name': 'Python Study Circle', 'privacy': 'public', 'max_members': 30},
            {'name': 'Django Developers Hub', 'privacy': 'public', 'max_members': 25},
            {'name': 'Data Science Learners', 'privacy': 'course', 'max_members': 20},
            {'name': 'Design Thinkers', 'privacy': 'private', 'max_members': 15},
        ]
        
        for i, template in enumerate(group_templates):
            course = courses[i % len(courses)] if i < len(courses) else courses[0]
            
            group, created = StudyGroup.objects.get_or_create(
                name=template['name'],
                defaults={
                    'description': f"A study group for {course.title} enthusiasts to collaborate and learn together.",
                    'creator': instructors[i % len(instructors)],
                    'course': course,
                    'privacy': template['privacy'],
                    'max_members': template['max_members'],
                    'is_active': True,
                    'member_count': random.randint(5, template['max_members'] - 5),
                    'message_count': random.randint(10, 100)
                }
            )
