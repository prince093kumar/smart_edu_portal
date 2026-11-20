from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.courses.models import Lesson
from apps.assessments.models import Submission
from apps.innovation.models import Idea, IdeaComment
from .models import Notification

@receiver(post_save, sender=Submission)
def notify_on_graded(sender, instance, created, **kwargs):
    if not created and instance.marks is not None:
        Notification.objects.create(
            user=instance.student,
            message=f"Your assignment '{instance.assignment.title}' was graded: {instance.marks}/{instance.assignment.max_marks}.",
            link=f"/assessments/assignment/{instance.assignment.id}/",
        )

@receiver(post_save, sender=Idea)
def notify_on_idea_status(sender, instance, created, **kwargs):
    if not created and instance.status != 'submitted':
        Notification.objects.create(
            user=instance.author,
            message=f"Status update on your idea '{instance.title}': {instance.get_status_display()}.",
            link=f"/innovation/{instance.id}/",
        )

@receiver(post_save, sender=IdeaComment)
def notify_on_idea_comment(sender, instance, created, **kwargs):
    if created and instance.idea.author != instance.user:
        Notification.objects.create(
            user=instance.idea.author,
            message=f"{instance.user.username} commented on your idea '{instance.idea.title}'.",
            link=f"/innovation/{instance.idea.id}/",
        )
