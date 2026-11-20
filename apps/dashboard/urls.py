from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('student/', views.student_dashboard, name='student'),
    path('teacher/', views.teacher_dashboard, name='teacher'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('admin/verify-teacher/<int:user_id>/', views.verify_teacher, name='verify_teacher'),
    path('admin/unverify-teacher/<int:user_id>/', views.unverify_teacher, name='unverify_teacher'),
    path('admin/approve-course/<int:course_id>/', views.approve_course, name='approve_course'),
    path('admin/reject-course/<int:course_id>/', views.reject_course, name='reject_course'),
]
