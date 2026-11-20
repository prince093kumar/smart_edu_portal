from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, StudentProfileForm, TeacherProfileForm, UserUpdateForm
from .models import StudentProfile, TeacherProfile

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'student':
                StudentProfile.objects.create(user=user)
            elif user.role == 'teacher':
                TeacherProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome to Smart Education, {user.first_name or user.username}!')
            return redirect('dashboard:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = '/'


@login_required
def profile(request):
    profile_obj = None
    if request.user.is_student:
        profile_obj, _ = StudentProfile.objects.get_or_create(user=request.user)
    elif request.user.is_teacher:
        profile_obj, _ = TeacherProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {'user': request.user, 'profile': profile_obj})


@login_required
def profile_edit(request):
    profile_obj = None
    profile_form = None
    if request.user.is_student:
        profile_obj, _ = StudentProfile.objects.get_or_create(user=request.user)
        profile_form_class = StudentProfileForm
    elif request.user.is_teacher:
        profile_obj, _ = TeacherProfile.objects.get_or_create(user=request.user)
        profile_form_class = TeacherProfileForm
    else:
        profile_form_class = None

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if profile_form_class and profile_obj:
            profile_form = profile_form_class(request.POST, request.FILES, instance=profile_obj)
        
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        if profile_form_class and profile_obj:
            profile_form = profile_form_class(instance=profile_obj)

    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })
