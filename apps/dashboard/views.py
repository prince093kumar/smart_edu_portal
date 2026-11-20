from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.courses.models import Course, Enrollment, LessonProgress
from apps.assessments.models import Attempt, Submission, Assignment, Quiz
from apps.innovation.models import Idea, IdeaVote
from apps.accounts.models import User

@login_required
def dashboard_home(request):
    if request.user.is_admin_user:
        return redirect('dashboard:admin')
    elif request.user.is_teacher:
        return redirect('dashboard:teacher')
    else:
        return redirect('dashboard:student')


@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    enrolled_courses = []
    for enr in enrollments:
        progress = enr.course.get_progress(request.user)
        enrolled_courses.append({
            'course': enr.course,
            'enrolled_on': enr.enrolled_on,
            'progress': progress,
        })

    recent_attempts = Attempt.objects.filter(student=request.user).select_related('quiz__course')[:5]
    recent_submissions = Submission.objects.filter(student=request.user).select_related('assignment__course')[:5]
    my_ideas = Idea.objects.filter(author=request.user).prefetch_related('votes')[:5]

    # Calculations for summary stats
    completed_courses_count = sum(1 for c in enrolled_courses if c['progress'] >= 100)
    avg_quiz_score = round(sum(a.score for a in recent_attempts) / len(recent_attempts), 1) if recent_attempts else 0

    return render(request, 'dashboard/student.html', {
        'enrolled_courses': enrolled_courses,
        'recent_attempts': recent_attempts,
        'recent_submissions': recent_submissions,
        'my_ideas': my_ideas,
        'completed_courses_count': completed_courses_count,
        'avg_quiz_score': avg_quiz_score,
    })


@login_required
def teacher_dashboard(request):
    if not (request.user.is_teacher or request.user.is_superuser):
        return redirect('dashboard:student')

    courses = Course.objects.filter(teacher=request.user)
    total_students = Enrollment.objects.filter(course__in=courses).values('student').distinct().count()
    
    pending_submissions = Submission.objects.filter(
        assignment__course__in=courses,
        marks__isnull=True
    ).select_related('assignment', 'student')[:10]

    pending_ideas = Idea.objects.filter(
        course__in=courses,
        status='submitted'
    ).select_related('author', 'course')[:5]

    total_quizzes = Quiz.objects.filter(course__in=courses).count()

    return render(request, 'dashboard/teacher.html', {
        'courses': courses,
        'total_students': total_students,
        'pending_submissions': pending_submissions,
        'pending_ideas': pending_ideas,
        'total_quizzes': total_quizzes,
    })


@login_required
def admin_dashboard(request):
    if not (request.user.is_admin_user or request.user.is_superuser):
        return redirect('dashboard:home')

    total_users = User.objects.count()
    total_students = User.objects.filter(role='student').count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_courses = Course.objects.count()
    total_ideas = Idea.objects.count()
    total_attempts = Attempt.objects.count()
    total_submissions = Submission.objects.count()

    recent_users = User.objects.order_by('-date_joined')[:6]
    recent_ideas = Idea.objects.select_related('author').order_by('-created_on')[:6]

    return render(request, 'dashboard/admin.html', {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'total_ideas': total_ideas,
        'total_attempts': total_attempts,
        'total_submissions': total_submissions,
        'recent_users': recent_users,
        'recent_ideas': recent_ideas,
    })
