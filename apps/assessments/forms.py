from django import forms
from .models import Quiz, Question, Choice, Assignment, Submission

TW_INPUT = (
    "w-full px-3 py-2 text-sm rounded-md border border-[var(--border)] "
    "bg-[var(--card)] text-[var(--foreground)] placeholder-[var(--muted-foreground)] "
    "focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition"
)

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'time_limit', 'pass_marks']
        widgets = {
            'title': forms.TextInput(attrs={'class': TW_INPUT}),
            'description': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 3}),
            'time_limit': forms.NumberInput(attrs={'class': TW_INPUT}),
            'pass_marks': forms.NumberInput(attrs={'class': TW_INPUT}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'marks']
        widgets = {
            'text': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 3}),
            'marks': forms.NumberInput(attrs={'class': TW_INPUT}),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': TW_INPUT}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded text-[var(--primary)] focus:ring-[var(--primary)]'}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'max_marks', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': TW_INPUT}),
            'description': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'class': TW_INPUT, 'type': 'datetime-local'}),
            'max_marks': forms.NumberInput(attrs={'class': TW_INPUT}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 3, 'placeholder': 'Optional notes for your instructor...'}),
        }


class GradingForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['marks', 'feedback']
        widgets = {
            'marks': forms.NumberInput(attrs={'class': TW_INPUT}),
            'feedback': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 4, 'placeholder': 'Constructive feedback for the student...'}),
        }
