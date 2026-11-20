from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.courses.models import Course, Enrollment
from apps.assessments.models import Quiz, Question, Choice, Attempt, Assignment, Submission

class AssessmentTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher_eval', email='teval@test.com', password='pass', role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username='student_eval', email='seval@test.com', password='pass', role=User.Role.STUDENT
        )
        self.course = Course.objects.create(title='Python Fundamentals', teacher=self.teacher, is_published=True)
        Enrollment.objects.create(student=self.student, course=self.course)

    def test_quiz_taking_and_scoring(self):
        quiz = Quiz.objects.create(course=self.course, title='Syntax Quiz', pass_marks=50)
        q1 = Question.objects.create(quiz=quiz, text='What is bool(0)?', marks=1)
        c1 = Choice.objects.create(question=q1, text='False', is_correct=True)
        c2 = Choice.objects.create(question=q1, text='True', is_correct=False)

        self.client.login(username='student_eval', password='pass')
        response = self.client.post(reverse('assessments:take_quiz', args=[quiz.id]), {
            f'question_{q1.id}': c1.id,
        })
        self.assertEqual(response.status_code, 302)
        
        attempt = Attempt.objects.filter(student=self.student, quiz=quiz).first()
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.score, 1)
        self.assertTrue(attempt.passed)

    def test_assignment_and_grading(self):
        assignment = Assignment.objects.create(
            course=self.course,
            title='Build a CLI',
            description='Build a command line app in Python.',
            due_date=timezone.now() + timedelta(days=5),
            max_marks=50,
        )

        # Student submission
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_file = SimpleUploadedFile("solution.pdf", b"%PDF-1.4 dummy file content", content_type="application/pdf")
        
        self.client.login(username='student_eval', password='pass')
        res = self.client.post(reverse('assessments:assignment_detail', args=[assignment.id]), {
            'file': test_file,
            'remarks': 'Attached solution',
        })
        self.assertEqual(res.status_code, 302)
        
        submission = Submission.objects.filter(assignment=assignment, student=self.student).first()
        self.assertIsNotNone(submission)

        # Teacher grades the submission
        self.client.login(username='teacher_eval', password='pass')
        grade_res = self.client.post(reverse('assessments:grade_submission', args=[submission.id]), {
            'marks': 48,
            'feedback': 'Excellent clean architecture!',
        })
        self.assertEqual(grade_res.status_code, 302)
        
        submission.refresh_from_db()
        self.assertEqual(submission.marks, 48)
        self.assertEqual(submission.graded_by, self.teacher)
