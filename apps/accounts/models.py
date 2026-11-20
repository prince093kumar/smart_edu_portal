from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_verified_teacher(self):
        if self.is_superuser:
            return True
        if not self.is_teacher:
            return False
        return hasattr(self, 'teacher_profile') and self.teacher_profile.is_verified


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    institution = models.CharField(max_length=200, blank=True)
    class_name = models.CharField(max_length=100, blank=True, verbose_name='Grade / Class')
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"Student: {self.user.username}"


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.CharField(max_length=200, blank=True)
    qualification = models.CharField(max_length=300, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Verified by Admin',
        help_text='Teacher must be verified by an administrator before they can create courses.'
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        status = 'Verified' if self.is_verified else 'Pending Verification'
        return f"Teacher: {self.user.username} ({status})"
