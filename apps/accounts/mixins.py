from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import redirect

class StudentRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_student

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Only students can access this section.")
        return super().handle_no_permission()


class TeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_teacher or self.request.user.is_superuser)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Only instructors/teachers can access this section.")
        return super().handle_no_permission()


class VerifiedTeacherRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Requires the user to be a verified instructor (or platform administrator).
    Unverified instructors are redirected to their course list with an alert.
    """
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.is_verified_teacher

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_teacher and not self.request.user.is_verified_teacher:
                messages.warning(
                    self.request,
                    "Your instructor account is pending administrator verification. You cannot create courses until an admin verifies your status."
                )
                return redirect('courses:teacher_courses')
            raise PermissionDenied("Only verified instructors can access this section.")
        return super().handle_no_permission()


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin_user

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Only platform administrators can access this section.")
        return super().handle_no_permission()
