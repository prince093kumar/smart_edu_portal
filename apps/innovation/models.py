from django.db import models
from django.conf import settings
from apps.courses.models import Course
from apps.common.validators import validate_file_size, validate_document_extension

class Idea(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = 'submitted', 'Submitted'
        UNDER_REVIEW = 'under_review', 'Under Review'
        APPROVED = 'approved', 'Approved'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        REJECTED = 'rejected', 'Archived / Rejected'

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ideas',
    )
    title = models.CharField(max_length=200)
    problem = models.TextField(help_text='What real-world problem does this idea address?')
    solution = models.TextField(help_text='How does your proposal solve it?')
    category = models.CharField(max_length=100, default='General Technology', help_text='e.g., AI/ML, EdTech, IoT, Sustainability')
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_ideas',
        help_text='Optionally link this idea to a course you studied'
    )
    file = models.FileField(
        upload_to='idea_files/', blank=True, null=True, 
        help_text='Proposal PDF, architecture diagram, etc.',
        validators=[validate_file_size, validate_document_extension]
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    mentor_feedback = models.TextField(blank=True, help_text='Notes and mentorship guidance from faculty')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    @property
    def total_votes(self):
        return self.votes.count()


class IdeaComment(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.idea.title}"


class IdeaVote(models.Model):
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='idea_votes')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('idea', 'user')

    def __str__(self):
        return f"{self.user.username} voted for {self.idea.title}"
