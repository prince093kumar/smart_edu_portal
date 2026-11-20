from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('my-courses/', views.teacher_courses, name='teacher_courses'),
    path('create/', views.CourseCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.course_detail, name='detail'),
    path('<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='edit'),
    path('<slug:slug>/enroll/', views.enroll, name='enroll'),
    path('<slug:slug>/add-module/', views.add_module, name='add_module'),
    path('<slug:slug>/module/<int:module_id>/add-lesson/', views.add_lesson, name='add_lesson'),
    path('<slug:slug>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson'),
    path('<slug:slug>/lesson/<int:lesson_id>/complete/', views.mark_complete, name='mark_complete'),
]
