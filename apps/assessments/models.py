from django.db import models
from django.conf import settings
from apps.courses.models import Course
from apps.common.validators import validate_file_size, validate_document_extension

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    time_limit = models.PositiveIntegerField(default=15, help_text='Time limit in minutes (0 for no limit)')
    pass_marks = models.PositiveIntegerField(default=50, help_text='Passing percentage (e.g. 50)')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def total_marks(self):
        return sum(q.marks for q in self.questions.all()) or 1


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Q: {self.text[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Wrong'})"


class Attempt(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.FloatField()
    total_marks = models.FloatField(default=100)
    passed = models.BooleanField(default=False)
    taken_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-taken_on']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}: {self.score}/{self.total_marks}"


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=100)
    file = models.FileField(
        upload_to='assignment_files/', blank=True, null=True, 
        help_text='Reference materials / brief',
        validators=[validate_file_size, validate_document_extension]
    )
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    file = models.FileField(
        upload_to='submissions/',
        validators=[validate_file_size, validate_document_extension]
    )
    remarks = models.TextField(blank=True, help_text='Student comments or notes')
    submitted_on = models.DateTimeField(auto_now_add=True)
    marks = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions',
    )
    graded_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_on']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
