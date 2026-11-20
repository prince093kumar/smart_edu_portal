from django import forms
from .models import Course, Module, Lesson

TW_INPUT = (
    "w-full px-3 py-2 text-sm rounded-md border border-[var(--border)] "
    "bg-[var(--card)] text-[var(--foreground)] placeholder-[var(--muted-foreground)] "
    "focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition"
)

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'thumbnail', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': TW_INPUT}),
            'description': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 4}),
            'category': forms.Select(attrs={'class': TW_INPUT}),
            'is_published': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded text-[var(--primary)] focus:ring-[var(--primary)]'}),
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': TW_INPUT}),
            'order': forms.NumberInput(attrs={'class': TW_INPUT}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_url', 'file', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': TW_INPUT}),
            'content': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 6}),
            'video_url': forms.URLInput(attrs={'class': TW_INPUT, 'placeholder': 'https://www.youtube.com/watch?v=...'}),
            'order': forms.NumberInput(attrs={'class': TW_INPUT}),
        }
