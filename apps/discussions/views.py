from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.courses.models import Course, Enrollment
from .models import Thread, Post
from .forms import ThreadForm, PostForm

def thread_list(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    threads = course.threads.select_related('author').prefetch_related('posts').all()
    return render(request, 'discussions/thread_list.html', {
        'course': course,
        'threads': threads,
    })


@login_required
def create_thread(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    # Check enrollment if student
    if request.user.is_student and not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'Please enroll in the course to participate in the forum.')
        return redirect('courses:detail', slug=course.slug)

    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.course = course
            thread.author = request.user
            thread.save()
            messages.success(request, 'Discussion topic opened!')
            return redirect('discussions:detail', course_slug=course.slug, thread_id=thread.id)
    else:
        form = ThreadForm()
    return render(request, 'discussions/thread_form.html', {'form': form, 'course': course})


def thread_detail(request, course_slug, thread_id):
    course = get_object_or_404(Course, slug=course_slug)
    thread = get_object_or_404(Thread, id=thread_id, course=course)
    posts = thread.posts.select_related('author').all()
    form = PostForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to reply.')
            return redirect('accounts:login')

        if thread.is_closed:
            messages.error(request, 'This discussion is marked as closed.')
            return redirect('discussions:detail', course_slug=course.slug, thread_id=thread.id)

        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.save()
            messages.success(request, 'Reply posted!')
            return redirect('discussions:detail', course_slug=course.slug, thread_id=thread.id)

    return render(request, 'discussions/thread_detail.html', {
        'course': course,
        'thread': thread,
        'posts': posts,
        'form': form,
    })
