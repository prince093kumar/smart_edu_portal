from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, StudentProfile, TeacherProfile

TW_INPUT = (
    "w-full px-3 py-2 text-sm rounded-md border border-[var(--border)] "
    "bg-[var(--card)] text-[var(--foreground)] placeholder-[var(--muted-foreground)] "
    "focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition"
)

class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[('student', 'Student'), ('teacher', 'Teacher')],
        widget=forms.RadioSelect(attrs={'class': 'text-[var(--primary)] focus:ring-[var(--primary)]'}),
        initial='student',
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'role':
                field.widget.attrs.update({'class': TW_INPUT})


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': TW_INPUT})


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['institution', 'class_name', 'bio', 'photo']
        widgets = {
            'institution': forms.TextInput(attrs={'class': TW_INPUT}),
            'class_name': forms.TextInput(attrs={'class': TW_INPUT}),
            'bio': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 3}),
        }


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['department', 'qualification', 'bio', 'photo']
        widgets = {
            'department': forms.TextInput(attrs={'class': TW_INPUT}),
            'qualification': forms.TextInput(attrs={'class': TW_INPUT}),
            'bio': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 3}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': TW_INPUT}),
            'last_name': forms.TextInput(attrs={'class': TW_INPUT}),
            'email': forms.EmailInput(attrs={'class': TW_INPUT}),
        }
