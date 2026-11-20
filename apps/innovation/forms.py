from django import forms
from .models import Idea, IdeaComment

TW_INPUT = (
    "w-full px-3 py-2 text-sm rounded-md border border-[var(--border)] "
    "bg-[var(--card)] text-[var(--foreground)] placeholder-[var(--muted-foreground)] "
    "focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition"
)

class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['title', 'problem', 'solution', 'category', 'course', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'e.g. Smart Attendance via Computer Vision'}),
            'problem': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 4, 'placeholder': 'Explain the exact pain point or limitation...'}),
            'solution': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 5, 'placeholder': 'Outline your technical/practical solution and implementation steps...'}),
            'category': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'e.g. IoT, Clean Energy, Web3, Healthcare'}),
            'course': forms.Select(attrs={'class': TW_INPUT}),
        }


class IdeaCommentForm(forms.ModelForm):
    class Meta:
        model = IdeaComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 3, 'placeholder': 'Leave peer feedback, suggestion or offer collaboration...'}),
        }


class MentorStatusForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ['status', 'mentor_feedback']
        widgets = {
            'status': forms.Select(attrs={'class': TW_INPUT}),
            'mentor_feedback': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 4, 'placeholder': 'Provide guidance, mentorship suggestions, or approval notes...'}),
        }
