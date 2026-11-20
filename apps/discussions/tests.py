from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User
from apps.courses.models import Course, Enrollment
from apps.discussions.models import Thread, Post

class DiscussionTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='prof_disc', email='pdisc@test.com', password='pass', role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username='stud_disc', email='sdisc@test.com', password='pass', role=User.Role.STUDENT
        )
        self.course = Course.objects.create(title='Operating Systems', teacher=self.teacher, is_published=True)
        Enrollment.objects.create(student=self.student, course=self.course)

    def test_thread_and_post_creation(self):
        self.client.login(username='stud_disc', password='pass')
        res = self.client.post(reverse('discussions:create', args=[self.course.slug]), {
            'title': 'Difference between Process and Thread?',
            'content': 'Can someone clarify memory sharing between threads?',
        })
        self.assertEqual(res.status_code, 302)
        
        thread = Thread.objects.filter(course=self.course, title='Difference between Process and Thread?').first()
        self.assertIsNotNone(thread)
        self.assertEqual(thread.author, self.student)

        # Teacher replies to thread
        self.client.login(username='prof_disc', password='pass')
        reply_res = self.client.post(reverse('discussions:detail', args=[self.course.slug, thread.id]), {
            'body': 'Threads within the same process share heap memory, but have independent call stacks.',
        })
        self.assertEqual(reply_res.status_code, 302)
        self.assertEqual(thread.total_replies, 1)
