from django.test import TestCase
from apps.accounts.models import User
from apps.courses.models import Course, Module, Lesson, Enrollment, LessonProgress
from apps.assessments.models import Quiz, Question, Choice, Attempt
from apps.innovation.models import Idea, IdeaVote

class SmartEducationCoreTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='t1', email='teacher1@test.com', password='pass', role=User.Role.TEACHER
        )
        self.student = User.objects.create_user(
            username='s1', email='student1@test.com', password='pass', role=User.Role.STUDENT
        )
        self.course = Course.objects.create(title='Python Testing', teacher=self.teacher, is_published=True)
        self.module = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.lesson1 = Lesson.objects.create(module=self.module, title='Lesson 1', order=1)
        self.lesson2 = Lesson.objects.create(module=self.module, title='Lesson 2', order=2)

    def test_user_roles(self):
        self.assertTrue(self.teacher.is_teacher)
        self.assertFalse(self.teacher.is_student)
        self.assertTrue(self.student.is_student)
        self.assertFalse(self.student.is_teacher)

    def test_course_progress(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.assertEqual(self.course.get_progress(self.student), 0)

        LessonProgress.objects.create(student=self.student, lesson=self.lesson1, completed=True)
        self.assertEqual(self.course.get_progress(self.student), 50)

        LessonProgress.objects.create(student=self.student, lesson=self.lesson2, completed=True)
        self.assertEqual(self.course.get_progress(self.student), 100)

    def test_quiz_auto_grading(self):
        quiz = Quiz.objects.create(course=self.course, title='Test Quiz', pass_marks=50)
        q1 = Question.objects.create(quiz=quiz, text='What is 2+2?', marks=2)
        c1 = Choice.objects.create(question=q1, text='4', is_correct=True)
        c2 = Choice.objects.create(question=q1, text='5', is_correct=False)

        attempt = Attempt.objects.create(
            student=self.student,
            quiz=quiz,
            score=2,
            total_marks=2,
            passed=True,
        )
        self.assertTrue(attempt.passed)
        self.assertEqual(attempt.score, 2)

    def test_idea_voting_uniqueness(self):
        idea = Idea.objects.create(author=self.student, title='Clean Water AI', problem='Water scarcity', solution='IoT sensors')
        IdeaVote.objects.create(idea=idea, user=self.student)
        self.assertEqual(idea.total_votes, 1)

        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            IdeaVote.objects.create(idea=idea, user=self.student)
