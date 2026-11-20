from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/attempt/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    path('quiz/course/<slug:course_slug>/create/', views.create_quiz, name='create_quiz'),
    path('quiz/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('assignment/course/<slug:course_slug>/create/', views.create_assignment, name='create_assignment'),
    path('assignment/<int:assignment_id>/submissions/', views.submissions_list, name='submissions_list'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
]
