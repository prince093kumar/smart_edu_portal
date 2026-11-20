from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User

class AccountsTests(TestCase):
    def test_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newstudent',
            'email': 'newstudent@test.com',
            'role': 'student',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        # Redirects to dashboard after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        user = User.objects.get(username='newstudent')
        self.assertTrue(user.is_student)
        self.assertTrue(hasattr(user, 'student_profile'))

    def test_login(self):
        User.objects.create_user(username='logintest', email='login@test.com', password='password123', role='student')
        response = self.client.post(reverse('accounts:login'), {
            'username': 'logintest',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 302)
