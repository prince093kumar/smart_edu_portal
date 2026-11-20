from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.courses.models import Course, Enrollment
from .models import Quiz, Question, Choice, Attempt, Assignment, Submission
from .forms import QuizForm, QuestionForm, ChoiceForm, AssignmentForm, SubmissionForm, GradingForm

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course

    # Check student enrollment
    if request.user.is_student:
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.error(request, 'Please enroll in the course to attempt this quiz.')
            return redirect('courses:detail', slug=course.slug)

    questions = quiz.questions.prefetch_related('choices').all()

    if request.method == 'POST':
        total_quiz_marks = sum(q.marks for q in questions) or 1
        obtained_marks = 0
        user_answers = {}

        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}')
            if choice_id:
                user_answers[question.id] = int(choice_id)
                try:
                    selected_choice = Choice.objects.get(id=choice_id, question=question)
                    if selected_choice.is_correct:
                        obtained_marks += question.marks
                except Choice.DoesNotExist:
                    pass

        percentage = round((obtained_marks / total_quiz_marks) * 100, 1)
        is_passed = percentage >= quiz.pass_marks

        attempt = Attempt.objects.create(
            student=request.user,
            quiz=quiz,
            score=obtained_marks,
            total_marks=total_quiz_marks,
            passed=is_passed,
        )

        messages.success(request, f'Quiz submitted! Score: {obtained_marks}/{total_quiz_marks} ({percentage}%)')
        return redirect('assessments:quiz_result', attempt_id=attempt.id)

    return render(request, 'assessments/quiz_take.html', {
        'quiz': quiz,
        'course': course,
        'questions': questions,
    })


@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id)
    if attempt.student != request.user and not (request.user.is_teacher or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    percentage = round((attempt.score / attempt.total_marks) * 100, 1) if attempt.total_marks else 0
    return render(request, 'assessments/quiz_result.html', {
        'attempt': attempt,
        'percentage': percentage,
    })


@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course
    submission = None

    if request.user.is_student:
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()

    form = SubmissionForm(instance=submission) if submission else SubmissionForm()

    if request.method == 'POST' and request.user.is_student:
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = assignment
            sub.student = request.user
            sub.save()
            messages.success(request, 'Your assignment has been submitted successfully!')
            return redirect('assessments:assignment_detail', assignment_id=assignment.id)

    return render(request, 'assessments/assignment_detail.html', {
        'assignment': assignment,
        'course': course,
        'submission': submission,
        'form': form,
    })


# Teacher views
@login_required
def create_quiz(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, teacher=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            messages.success(request, 'Quiz created! Now add questions.')
            return redirect('assessments:add_question', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'assessments/quiz_form.html', {'form': form, 'course': course})


@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, course__teacher=request.user)
    if request.method == 'POST':
        q_text = request.POST.get('text')
        q_marks = int(request.POST.get('marks', 1))
        if q_text:
            question = Question.objects.create(quiz=quiz, text=q_text, marks=q_marks)
            # Create choices
            choice_texts = request.POST.getlist('choice_text')
            correct_idx = request.POST.get('correct_choice')
            for i, c_text in enumerate(choice_texts):
                if c_text.strip():
                    is_correct = (str(i) == str(correct_idx))
                    Choice.objects.create(question=question, text=c_text.strip(), is_correct=is_correct)
            messages.success(request, 'Question and choices added!')
            if 'save_and_add' in request.POST:
                return redirect('assessments:add_question', quiz_id=quiz.id)
            return redirect('courses:detail', slug=quiz.course.slug)
    return render(request, 'assessments/question_form.html', {'quiz': quiz})


@login_required
def create_assignment(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, teacher=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            messages.success(request, 'Assignment posted successfully!')
            return redirect('courses:detail', slug=course.slug)
    else:
        form = AssignmentForm()
    return render(request, 'assessments/assignment_form.html', {'form': form, 'course': course})


@login_required
def submissions_list(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course__teacher=request.user)
    submissions = assignment.submissions.select_related('student').all()
    return render(request, 'assessments/submissions_list.html', {
        'assignment': assignment,
        'submissions': submissions,
    })


@login_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, assignment__course__teacher=request.user)
    if request.method == 'POST':
        form = GradingForm(request.POST, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.graded_by = request.user
            sub.graded_on = timezone.now()
            sub.save()
            messages.success(request, f'Grade recorded for {sub.student.username}.')
            return redirect('assessments:submissions_list', assignment_id=submission.assignment.id)
    else:
        form = GradingForm(instance=submission)
    return render(request, 'assessments/grade_submission.html', {
        'submission': submission,
        'form': form,
    })
