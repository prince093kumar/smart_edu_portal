import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from apps.accounts.models import User, StudentProfile, TeacherProfile
from apps.courses.models import Category, Course, Module, Lesson, Enrollment, LessonProgress
from apps.assessments.models import Quiz, Question, Choice, Attempt, Assignment, Submission
from apps.innovation.models import Idea, IdeaComment, IdeaVote
from apps.discussions.models import Thread, Post
from apps.notifications.models import Notification

print("Starting database seeding...")

# 1. Users
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@smartedu.org',
        'first_name': 'System',
        'last_name': 'Administrator',
        'role': User.Role.ADMIN,
        'is_staff': True,
        'is_superuser': True,
    }
)
admin_user.set_password('admin123')
admin_user.save()

teacher_user, _ = User.objects.get_or_create(
    username='dr_sarah',
    defaults={
        'email': 'sarah@smartedu.org',
        'first_name': 'Dr. Sarah',
        'last_name': 'Jenkins',
        'role': User.Role.TEACHER,
        'is_staff': True,
    }
)
teacher_user.set_password('teacher123')
teacher_user.save()
TeacherProfile.objects.get_or_create(
    user=teacher_user,
    defaults={
        'department': 'Computer Science & AI',
        'qualification': 'Ph.D. in Machine Learning, MIT',
        'bio': 'Passionate about guiding students to convert academic research into impactful real-world innovations.'
    }
)

student1, _ = User.objects.get_or_create(
    username='alex_coder',
    defaults={
        'email': 'alex@smartedu.org',
        'first_name': 'Alex',
        'last_name': 'Rivera',
        'role': User.Role.STUDENT,
    }
)
student1.set_password('student123')
student1.save()
StudentProfile.objects.get_or_create(
    user=student1,
    defaults={
        'institution': 'Apex Institute of Technology',
        'class_name': 'B.Tech CS 3rd Year',
        'bio': 'Aspiring full-stack engineer and open-source enthusiast.'
    }
)

student2, _ = User.objects.get_or_create(
    username='priya_sharma',
    defaults={
        'email': 'priya@smartedu.org',
        'first_name': 'Priya',
        'last_name': 'Sharma',
        'role': User.Role.STUDENT,
    }
)
student2.set_password('student123')
student2.save()
StudentProfile.objects.get_or_create(
    user=student2,
    defaults={
        'institution': 'Delhi Engineering College',
        'class_name': 'B.Tech IT 4th Year',
        'bio': 'Building smart devices and AI models for rural agriculture.'
    }
)

# 2. Categories
cat_ai, _ = Category.objects.get_or_create(name='Artificial Intelligence', defaults={'description': 'Modern AI, Machine Learning, and Neural Networks'})
cat_web, _ = Category.objects.get_or_create(name='Web Development', defaults={'description': 'Full-stack application engineering with Django & modern frameworks'})
cat_iot, _ = Category.objects.get_or_create(name='IoT & Embedded Systems', defaults={'description': 'Sensors, microcontrollers, and hardware innovation'})

# 3. Courses
course1, _ = Course.objects.get_or_create(
    title='Full-Stack Web Engineering with Django 5 & Tailwind CSS',
    defaults={
        'teacher': teacher_user,
        'category': cat_web,
        'description': 'Master the Model-Template-View architecture, responsive design with Tailwind CSS, relational databases, REST APIs, and automated assessment workflows.',
        'is_published': True,
    }
)

# Modules & Lessons for Course 1
m1, _ = Module.objects.get_or_create(course=course1, title='Module 1: Django Architecture & Setup', order=1)
m2, _ = Module.objects.get_or_create(course=course1, title='Module 2: Models, ORM & Migrations', order=2)
m3, _ = Module.objects.get_or_create(course=course1, title='Module 3: Tailwind Styling & Dynamic Templates', order=3)

l1, _ = Lesson.objects.get_or_create(
    module=m1,
    title='Understanding Django MTV Pattern',
    defaults={
        'content': '''The Model-Template-View (MTV) pattern is Django's approach to software architecture:

1. **Model**: Defines your database schema using Python classes. Django handles migrations and SQL abstraction automatically.
2. **Template**: Presentation layer rendering HTML with Django Template Language (DTL).
3. **View**: The request-response handler fetching data from Models and passing it into Templates.

Understanding this separation makes maintaining large applications straightforward.''',
        'video_url': 'https://www.youtube.com/watch?v=rHux0gMZ3Eg',
        'order': 1,
    }
)

l2, _ = Lesson.objects.get_or_create(
    module=m1,
    title='Configuring Multi-Environment Settings & Decouple',
    defaults={
        'content': '''Professional Django projects separate development from production settings:

- `base.py`: Shared apps, middleware, and templates.
- `dev.py`: DEBUG=True, SQLite local database, console email backend.
- `prod.py`: DEBUG=False, PostgreSQL, strict SSL cookies, allowed hosts.

We use `python-decouple` to ensure credentials remain secure.''',
        'order': 2,
    }
)

l3, _ = Lesson.objects.get_or_create(
    module=m2,
    title='Designing Relational Models & Foreign Keys',
    defaults={
        'content': '''Foreign keys and unique constraints ensure data integrity.
For example, linking an `Enrollment` model with `unique_together = ('student', 'course')` prevents accidental duplicate enrollments.''',
        'order': 1,
    }
)

# 4. Enrollments & Progress
Enrollment.objects.get_or_create(student=student1, course=course1)
LessonProgress.objects.get_or_create(student=student1, lesson=l1, defaults={'completed': True, 'completed_on': timezone.now()})
LessonProgress.objects.get_or_create(student=student1, lesson=l2, defaults={'completed': True, 'completed_on': timezone.now()})

Enrollment.objects.get_or_create(student=student2, course=course1)
LessonProgress.objects.get_or_create(student=student2, lesson=l1, defaults={'completed': True, 'completed_on': timezone.now()})

# 5. Quiz & Questions
quiz1, _ = Quiz.objects.get_or_create(
    course=course1,
    title='Django Fundamentals & MTV Knowledge Check',
    defaults={
        'description': 'Test your comprehension of Django MTV pattern, ORM, and environment security.',
        'time_limit': 10,
        'pass_marks': 50,
    }
)

if not quiz1.questions.exists():
    q1 = Question.objects.create(quiz=quiz1, text='What does the "V" in Django\'s MTV architecture stand for?', marks=2)
    Choice.objects.create(question=q1, text='View (Request handler & business logic)', is_correct=True)
    Choice.objects.create(question=q1, text='Visual (CSS styling)', is_correct=False)
    Choice.objects.create(question=q1, text='Variable (Session state)', is_correct=False)
    Choice.objects.create(question=q1, text='Vector (Mathematical computing)', is_correct=False)

    q2 = Question.objects.create(quiz=quiz1, text='Which tool is used in Django to propagate model schema changes into the database?', marks=2)
    Choice.objects.create(question=q2, text='makemigrations and migrate', is_correct=True)
    Choice.objects.create(question=q2, text='db.sync()', is_correct=False)
    Choice.objects.create(question=q2, text='sql.update()', is_correct=False)
    Choice.objects.create(question=q2, text='schema.push()', is_correct=False)

# Sample Attempt
Attempt.objects.get_or_create(
    student=student1,
    quiz=quiz1,
    defaults={
        'score': 4,
        'total_marks': 4,
        'passed': True,
    }
)

# 6. Assignment
assign1, _ = Assignment.objects.get_or_create(
    course=course1,
    title='Capstone Lab 1: Implement Role-Based Access Control',
    defaults={
        'description': 'Create custom UserPassesTestMixin subclasses to restrict access to Instructor-only and Student-only dashboard endpoints. Include unit tests.',
        'due_date': timezone.now() + timedelta(days=7),
        'max_marks': 100,
    }
)

# 7. Innovation Hub Ideas
idea1, _ = Idea.objects.get_or_create(
    title='Smart Vision Attendance with Edge AI',
    defaults={
        'author': student1,
        'category': 'AI & Edge Computing',
        'course': course1,
        'problem': 'Manual attendance in lecture halls consumes 10-15 minutes of class time and is vulnerable to proxy attendance fraud.',
        'solution': 'Deploy a lightweight edge camera running a quantized MobileNetV3 facial identification pipeline with anti-spoofing liveness detection. Automatically syncs attendance records via Django REST endpoints to faculty dashboards in under 3 seconds.',
        'status': Idea.Status.IN_PROGRESS,
        'mentor_feedback': 'Strong technical design. Ensure you evaluate model accuracy under varying lecture room lighting conditions and add an opt-out privacy protocol.',
    }
)
IdeaVote.objects.get_or_create(idea=idea1, user=student1)
IdeaVote.objects.get_or_create(idea=idea1, user=student2)
IdeaVote.objects.get_or_create(idea=idea1, user=teacher_user)

IdeaComment.objects.get_or_create(
    idea=idea1,
    user=student2,
    defaults={'text': 'Great project! Are you planning to run inference on a Raspberry Pi 5 or an NVIDIA Jetson Nano? Would love to collaborate on the hardware enclosure.'}
)

idea2, _ = Idea.objects.get_or_create(
    title='AgriSense: IoT Soil Microbiome & Irrigation Controller',
    defaults={
        'author': student2,
        'category': 'IoT & Sustainability',
        'problem': 'Over-irrigation and unmeasured fertilizer runoff degrade topsoil fertility and deplete regional water tables in semi-arid farmlands.',
        'solution': 'A solar-powered LoRaWAN sensor node measuring soil NPK, volumetric water content, and temperature. An automated solar valve triggers drip irrigation only when root-zone moisture drops below optimal crop thresholds.',
        'status': Idea.Status.APPROVED,
        'mentor_feedback': 'Approved for departmental lab prototyping grant. Contact lab technician for LoRa gateway testing access.',
    }
)
IdeaVote.objects.get_or_create(idea=idea2, user=student2)
IdeaVote.objects.get_or_create(idea=idea2, user=student1)

# 8. Discussion Forum
thread1, _ = Thread.objects.get_or_create(
    course=course1,
    author=student1,
    title='Best practices for caching Tailwind CSS in production with WhiteNoise?',
    defaults={
        'content': 'When deploying to a production server, should we compile Tailwind styles via CLI during collectstatic, or serve them from a pre-built static directory?'
    }
)
Post.objects.get_or_create(
    thread=thread1,
    author=teacher_user,
    defaults={
        'body': 'Pre-compiling your minified CSS bundle during the build step and allowing WhiteNoise to gzip/brotli compress it is the recommended standard practice.'
    }
)

# 9. Notifications
Notification.objects.get_or_create(
    user=student1,
    message="Your idea 'Smart Vision Attendance with Edge AI' was updated to 'In Progress' with mentor feedback.",
    link=f"/innovation/{idea1.id}/",
)
Notification.objects.get_or_create(
    user=student2,
    message="Your idea 'AgriSense' was approved by Dr. Sarah Jenkins!",
    link=f"/innovation/{idea2.id}/",
)

print("Demo data successfully seeded!")
print("Credentials:")
print("  Admin:     admin / admin123")
print("  Teacher:   dr_sarah / teacher123")
print("  Student:   alex_coder / student123")
print("  Student:   priya_sharma / student123")
