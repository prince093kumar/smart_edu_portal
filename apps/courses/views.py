from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from apps.accounts.mixins import TeacherRequiredMixin, VerifiedTeacherRequiredMixin
from django.views.generic import CreateView, UpdateView
from .models import Course, Category, Module, Lesson, Enrollment, LessonProgress
from .forms import CourseForm, ModuleForm, LessonForm

def course_list(request):
    courses = Course.objects.filter(is_approved=True, is_published=True)
    categories = Category.objects.all()
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')

    if query:
        courses = courses.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    paginator = Paginator(courses, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'courses': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)

    # Unapproved or unpublished courses are restricted to instructor/author and superuser
    if not (course.is_approved and course.is_published):
        can_preview = (
            request.user.is_authenticated and 
            (request.user == course.teacher or request.user.is_superuser)
        )
        if not can_preview:
            messages.warning(request, 'This course is pending administrator approval before public release.')
            return redirect('courses:list')

    is_enrolled = False
    progress = 0

    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        if is_enrolled:
            progress = course.get_progress(request.user)

    modules = course.modules.prefetch_related('lessons').all()

    # Assessments & course-linked ideas
    quizzes = course.quizzes.all() if hasattr(course, 'quizzes') else []
    assignments = course.assignments.all() if hasattr(course, 'assignments') else []
    linked_ideas = course.linked_ideas.select_related('author').all()[:6]

    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'progress': progress,
        'quizzes': quizzes,
        'assignments': assignments,
        'linked_ideas': linked_ideas,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def enroll(request, slug):
    course = get_object_or_404(Course, slug=slug, is_approved=True, is_published=True)
    if request.user.is_student:
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        if created:
            messages.success(request, f'Successfully enrolled in "{course.title}"!')
        else:
            messages.info(request, f'You are already enrolled in "{course.title}".')
    else:
        messages.error(request, 'Only student accounts can enroll in courses.')
    return redirect('courses:detail', slug=slug)


@login_required
def lesson_detail(request, slug, lesson_id):
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)

    if request.user.is_student:
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.warning(request, 'Please enroll in the course to view lesson material.')
            return redirect('courses:detail', slug=slug)

    progress = None
    if request.user.is_student:
        progress, _ = LessonProgress.objects.get_or_create(student=request.user, lesson=lesson)

    # Next / prev navigation
    all_lessons = list(Lesson.objects.filter(module__course=course).order_by('module__order', 'order', 'id'))
    current_idx = all_lessons.index(lesson) if lesson in all_lessons else 0
    prev_lesson = all_lessons[current_idx - 1] if current_idx > 0 else None
    next_lesson = all_lessons[current_idx + 1] if current_idx < len(all_lessons) - 1 else None

    context = {
        'course': course,
        'lesson': lesson,
        'progress': progress,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
    }
    return render(request, 'courses/lesson_detail.html', context)


@login_required
def mark_complete(request, slug, lesson_id):
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)

    if request.user.is_student and request.method == 'POST':
        progress, _ = LessonProgress.objects.get_or_create(student=request.user, lesson=lesson)
        progress.completed = True
        progress.completed_on = timezone.now()
        progress.save()
        messages.success(request, f'Nice job! Lesson "{lesson.title}" marked as finished.')

    return redirect('courses:lesson', slug=slug, lesson_id=lesson_id)


# Teacher course management
class CourseCreateView(VerifiedTeacherRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        if self.request.user.is_superuser:
            form.instance.is_approved = True
            messages.success(self.request, 'Course created and approved by administrator!')
        else:
            form.instance.is_approved = False
            messages.info(
                self.request,
                'Course draft created! It is now pending administrator review and approval before becoming visible to students.'
            )
        return super().form_valid(form)

    def get_success_url(self):
        return f"/courses/{self.object.slug}/"


class CourseUpdateView(TeacherRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Course.objects.all()
        return Course.objects.filter(teacher=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Course updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return f"/courses/{self.object.slug}/"


@login_required
def add_module(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    if not request.user.is_verified_teacher:
        messages.warning(request, 'Your instructor account is pending administrator verification. You cannot modify curriculum.')
        return redirect('courses:teacher_courses')
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, f'Module "{module.title}" created!')
            return redirect('courses:detail', slug=slug)
    else:
        form = ModuleForm()
    return render(request, 'courses/module_form.html', {'form': form, 'course': course})


@login_required
def add_lesson(request, slug, module_id):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    module = get_object_or_404(Module, id=module_id, course=course)
    if not request.user.is_verified_teacher:
        messages.warning(request, 'Your instructor account is pending administrator verification. You cannot modify curriculum.')
        return redirect('courses:teacher_courses')
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, f'Lesson "{lesson.title}" added!')
            return redirect('courses:detail', slug=slug)
    else:
        form = LessonForm()
    return render(request, 'courses/lesson_form.html', {'form': form, 'course': course, 'module': module})


@login_required
def teacher_courses(request):
    if not (request.user.is_teacher or request.user.is_superuser):
        messages.error(request, 'Only teachers can access instructor view.')
        return redirect('dashboard:home')
    courses = Course.objects.filter(teacher=request.user)
    is_verified = request.user.is_verified_teacher
    return render(request, 'courses/teacher_courses.html', {
        'courses': courses,
        'is_verified': is_verified,
    })
