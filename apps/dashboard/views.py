from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.courses.models import Course, Enrollment, LessonProgress
from apps.assessments.models import Attempt, Submission, Assignment, Quiz
from apps.innovation.models import Idea, IdeaVote
from apps.accounts.models import User
from apps.notifications.models import Notification

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
    is_verified = request.user.is_verified_teacher

    return render(request, 'dashboard/teacher.html', {
        'courses': courses,
        'total_students': total_students,
        'pending_submissions': pending_submissions,
        'pending_ideas': pending_ideas,
        'total_quizzes': total_quizzes,
        'is_verified': is_verified,
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

    # Unverified instructors awaiting admin verification
    pending_teachers = User.objects.filter(
        role='teacher',
        teacher_profile__is_verified=False
    ).select_related('teacher_profile').order_by('-date_joined')

    # Courses awaiting admin approval
    pending_courses = Course.objects.filter(
        is_approved=False
    ).select_related('teacher', 'category').order_by('-created_on')

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
        'pending_teachers': pending_teachers,
        'pending_courses': pending_courses,
        'recent_users': recent_users,
        'recent_ideas': recent_ideas,
    })


@login_required
def verify_teacher(request, user_id):
    if not (request.user.is_admin_user or request.user.is_superuser):
        messages.error(request, 'Only administrators can verify instructors.')
        return redirect('dashboard:home')

    if request.method == 'POST':
        teacher_user = get_object_or_404(User, id=user_id, role='teacher')
        profile = getattr(teacher_user, 'teacher_profile', None)
        if profile:
            profile.is_verified = True
            profile.verified_at = timezone.now()
            profile.save()
            Notification.objects.create(
                user=teacher_user,
                message="Your instructor account has been verified by an administrator! You are now authorized to create and manage courses.",
                link="/courses/my-courses/"
            )
            messages.success(request, f"Instructor '{teacher_user.get_full_name() or teacher_user.username}' has been successfully verified.")
        else:
            messages.error(request, "Teacher profile not found.")
    return redirect('dashboard:admin')


@login_required
def unverify_teacher(request, user_id):
    if not (request.user.is_admin_user or request.user.is_superuser):
        messages.error(request, 'Only administrators can revoke verification.')
        return redirect('dashboard:home')

    if request.method == 'POST':
        teacher_user = get_object_or_404(User, id=user_id, role='teacher')
        profile = getattr(teacher_user, 'teacher_profile', None)
        if profile:
            profile.is_verified = False
            profile.save()
            messages.info(request, f"Verification revoked for instructor '{teacher_user.username}'.")
    return redirect('dashboard:admin')


@login_required
def approve_course(request, course_id):
    if not (request.user.is_admin_user or request.user.is_superuser):
        messages.error(request, 'Only administrators can approve courses.')
        return redirect('dashboard:home')

    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        course.is_approved = True
        course.is_published = True
        course.approved_by = request.user
        course.approved_at = timezone.now()
        course.save()
        Notification.objects.create(
            user=course.teacher,
            message=f"Your course '{course.title}' has been approved by the administrator and is now live for students!",
            link=f"/courses/{course.slug}/"
        )
        messages.success(request, f"Course '{course.title}' is now approved and live to public!")
    return redirect('dashboard:admin')


@login_required
def reject_course(request, course_id):
    if not (request.user.is_admin_user or request.user.is_superuser):
        messages.error(request, 'Only administrators can reject courses.')
        return redirect('dashboard:home')

    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        course.is_approved = False
        course.save()
        Notification.objects.create(
            user=course.teacher,
            message=f"Your course '{course.title}' was reviewed by an administrator and marked unapproved. Please update the curriculum.",
            link=f"/courses/{course.slug}/"
        )
        messages.info(request, f"Course '{course.title}' marked unapproved.")
    return redirect('dashboard:admin')
