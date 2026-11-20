from django import forms
from .models import Thread, Post

TW_INPUT = (
    "w-full px-3 py-2 text-sm rounded-md border border-[var(--border)] "
    "bg-[var(--card)] text-[var(--foreground)] placeholder-[var(--muted-foreground)] "
    "focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition"
)

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': TW_INPUT, 'placeholder': 'Ask a question or start a topic...'}),
            'content': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 5, 'placeholder': 'Detailed explanation or context...'}),
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': TW_INPUT, 'rows': 3, 'placeholder': 'Write your reply...'}),
        }
