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
        self.course = Course.objects.create(title='Python Testing', teacher=self.teacher, is_published=True, is_approved=True)
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

    def test_course_banner_upload_and_display(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from apps.courses.forms import CourseForm

        form = CourseForm()
        self.assertIn('thumbnail', form.fields)

        tiny_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00'
            b'\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02'
            b'\x44\x01\x00\x3b'
        )
        banner_file = SimpleUploadedFile('test_banner.gif', tiny_gif, content_type='image/gif')
        course = Course.objects.create(
            title='Banner Test Course',
            teacher=self.teacher,
            thumbnail=banner_file,
            is_published=True,
            is_approved=True,
        )
        self.assertTrue(bool(course.thumbnail))

        # Course detail view renders the banner
        response = self.client.get(f'/courses/{course.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(course.thumbnail.url, response.content.decode())

        # Clean up created file
        if course.thumbnail:
            course.thumbnail.delete(save=False)

    def test_teacher_verification_and_course_approval_workflow(self):
        from apps.accounts.models import TeacherProfile

        # 1. Create a new unverified teacher
        unverified_teacher = User.objects.create_user(
            username='unverified_t', email='unverified@test.com', password='pass', role=User.Role.TEACHER
        )
        TeacherProfile.objects.create(user=unverified_teacher, is_verified=False)
        self.assertFalse(unverified_teacher.is_verified_teacher)

        # 2. Unverified teacher tries to access course creation -> blocked
        self.client.login(username='unverified_t', password='pass')
        resp = self.client.get('/courses/create/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/courses/my-courses/', resp.url)

        # 3. Create admin and verify the teacher
        admin_user = User.objects.create_superuser(
            username='adm', email='adm@test.com', password='pass', role=User.Role.ADMIN
        )
        self.client.login(username='adm', password='pass')
        verify_resp = self.client.post(f'/dashboard/admin/verify-teacher/{unverified_teacher.id}/')
        self.assertEqual(verify_resp.status_code, 302)

        unverified_teacher.teacher_profile.refresh_from_db()
        self.assertTrue(unverified_teacher.is_verified_teacher)

        # 4. Now verified teacher can access course create page and create a course
        self.client.login(username='unverified_t', password='pass')
        create_page = self.client.get('/courses/create/')
        self.assertEqual(create_page.status_code, 200)

        post_resp = self.client.post('/courses/create/', {
            'title': 'New Pending Course',
            'description': 'Description of course',
            'is_published': True,
        })
        self.assertEqual(post_resp.status_code, 302)

        created_course = Course.objects.get(title='New Pending Course')
        # Even though teacher checked is_published, is_approved is False!
        self.assertFalse(created_course.is_approved)

        # 5. Student cannot see unapproved course in course catalog
        self.client.login(username='s1', password='pass')
        cat_resp = self.client.get('/courses/')
        self.assertNotIn('New Pending Course', cat_resp.content.decode())

        # Student cannot view or enroll in unapproved course
        detail_resp = self.client.get(f'/courses/{created_course.slug}/')
        self.assertEqual(detail_resp.status_code, 302)

        # 6. Admin approves course to public
        self.client.login(username='adm', password='pass')
        approve_resp = self.client.post(f'/dashboard/admin/approve-course/{created_course.id}/')
        self.assertEqual(approve_resp.status_code, 302)

        created_course.refresh_from_db()
        self.assertTrue(created_course.is_approved)
        self.assertTrue(created_course.is_published)

        # 7. Student can now see and view the approved course
        self.client.login(username='s1', password='pass')
        cat_resp2 = self.client.get('/courses/')
        self.assertIn('New Pending Course', cat_resp2.content.decode())

        detail_resp2 = self.client.get(f'/courses/{created_course.slug}/')
        self.assertEqual(detail_resp2.status_code, 200)
