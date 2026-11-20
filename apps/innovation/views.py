from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import Idea, IdeaComment, IdeaVote
from .forms import IdeaForm, IdeaCommentForm, MentorStatusForm

def idea_list(request):
    ideas = Idea.objects.annotate(vote_count=Count('votes')).select_related('author', 'course')
    
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', 'votes')

    if query:
        ideas = ideas.filter(
            Q(title__icontains=query) | Q(problem__icontains=query) | Q(solution__icontains=query) | Q(category__icontains=query)
        )
    if status_filter:
        ideas = ideas.filter(status=status_filter)

    if sort_by == 'recent':
        ideas = ideas.order_by('-created_on')
    else:
        ideas = ideas.order_by('-vote_count', '-created_on')

    # Leaderboard top 5
    leaderboard = Idea.objects.annotate(vote_count=Count('votes')).order_by('-vote_count')[:5]

    paginator = Paginator(ideas, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user_voted_ids = []
    if request.user.is_authenticated:
        user_voted_ids = list(IdeaVote.objects.filter(user=request.user).values_list('idea_id', flat=True))

    return render(request, 'innovation/idea_list.html', {
        'ideas': page_obj,
        'page_obj': page_obj,
        'leaderboard': leaderboard,
        'user_voted_ids': user_voted_ids,
        'query': query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'statuses': Idea.Status.choices,
    })


def idea_detail(request, idea_id):
    idea = get_object_or_404(Idea.objects.select_related('author', 'course'), id=idea_id)
    comments = idea.comments.select_related('user').all()
    user_has_voted = False
    if request.user.is_authenticated:
        user_has_voted = IdeaVote.objects.filter(idea=idea, user=request.user).exists()

    comment_form = IdeaCommentForm()
    mentor_form = MentorStatusForm(instance=idea) if (request.user.is_authenticated and (request.user.is_teacher or request.user.is_superuser)) else None

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in first.')
            return redirect('accounts:login')

        if 'submit_comment' in request.POST:
            comment_form = IdeaCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.idea = idea
                comment.user = request.user
                comment.save()
                messages.success(request, 'Comment added!')
                return redirect('innovation:detail', idea_id=idea.id)

        elif 'update_status' in request.POST and (request.user.is_teacher or request.user.is_superuser):
            mentor_form = MentorStatusForm(request.POST, instance=idea)
            if mentor_form.is_valid():
                mentor_form.save()
                messages.success(request, f'Idea status updated to {idea.get_status_display()}!')
                return redirect('innovation:detail', idea_id=idea.id)

    return render(request, 'innovation/idea_detail.html', {
        'idea': idea,
        'comments': comments,
        'user_has_voted': user_has_voted,
        'comment_form': comment_form,
        'mentor_form': mentor_form,
    })


@login_required
def idea_create(request):
    if request.method == 'POST':
        form = IdeaForm(request.POST, request.FILES)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.author = request.user
            idea.save()
            messages.success(request, 'Your innovative project idea has been submitted!')
            return redirect('innovation:detail', idea_id=idea.id)
    else:
        form = IdeaForm()
    return render(request, 'innovation/idea_form.html', {'form': form})


@login_required
def idea_vote_toggle(request, idea_id):
    idea = get_object_or_404(Idea, id=idea_id)
    vote = IdeaVote.objects.filter(idea=idea, user=request.user).first()
    if vote:
        vote.delete()
        messages.info(request, f'Vote removed for "{idea.title}"')
    else:
        IdeaVote.objects.create(idea=idea, user=request.user)
        messages.success(request, f'Upvoted "{idea.title}"!')
    return redirect(request.META.get('HTTP_REFERER', 'innovation:list'))
