from django.contrib import admin
from .models import Idea, IdeaComment, IdeaVote

@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_on')
    list_filter = ('status', 'category')
    search_fields = ('title', 'problem', 'solution')

@admin.register(IdeaComment)
class IdeaCommentAdmin(admin.ModelAdmin):
    list_display = ('idea', 'user', 'created_on')

@admin.register(IdeaVote)
class IdeaVoteAdmin(admin.ModelAdmin):
    list_display = ('idea', 'user', 'created_on')
