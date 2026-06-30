from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Prompt, Domain, Comment
from .forms import PromptForm, CommentForm

STATIC_VERSION = 1.0

def access_denied(request):
    return render(request, 'prompts/access_denied.html', {'STATIC_VERSION': STATIC_VERSION})


def home(request):
    """Homepage with featured and recent prompts"""
    recent_prompts = Prompt.objects.filter(visibility='public').select_related('author', 'domain').annotate(
        upvote_count=Count('upvotes')
    ).prefetch_related('upvotes')[:6]

    top_prompts = Prompt.objects.filter(visibility='public').annotate(
        upvote_count=Count('upvotes')
    ).prefetch_related('upvotes').order_by('-upvote_count')[:6]

    domains = Domain.objects.all()

    context = {
        'recent_prompts': recent_prompts,
        'top_prompts': top_prompts,
        'domains': domains,
        'STATIC_VERSION': STATIC_VERSION,
    }
    return render(request, 'prompts/home.html', context)


def prompt_list(request):
    """List all prompts with filtering and search"""
    prompts = Prompt.objects.filter(visibility='public').select_related('author', 'domain').annotate(
        upvote_count=Count('upvotes')
    ).prefetch_related('upvotes')

    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        prompts = prompts.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    # Filter by domain
    domain_slug = request.GET.get('domain', '')
    if domain_slug:
        prompts = prompts.filter(domain__slug=domain_slug)

    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by == 'popular':
        prompts = prompts.order_by('-upvote_count')
    else:
        prompts = prompts.order_by(sort_by)

    domains = Domain.objects.all()

    context = {
        'prompts': prompts,
        'domains': domains,
        'search_query': search_query,
        'current_domain': domain_slug,
        'current_sort': sort_by,
        'STATIC_VERSION': STATIC_VERSION,
    }
    return render(request, 'prompts/prompt_list.html', context)


def prompt_detail(request, slug):
    """Detailed view of a single prompt"""
    prompt = get_object_or_404(
        Prompt.objects.select_related('author', 'domain').annotate(
            upvote_count=Count('upvotes')
        ),
        slug=slug
    )
    comments = prompt.comments.select_related('author').all()

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.prompt = prompt
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('prompt_detail', slug=slug)
    else:
        comment_form = CommentForm()

    is_upvoted = request.user.is_authenticated and prompt.upvotes.filter(id=request.user.id).exists()
    is_favorited = request.user.is_authenticated and prompt.favorites.filter(id=request.user.id).exists()

    context = {
        'prompt': prompt,
        'comments': comments,
        'comment_form': comment_form,
        'is_upvoted': is_upvoted,
        'is_favorited': is_favorited,
        'STATIC_VERSION': STATIC_VERSION,
    }
    return render(request, 'prompts/prompt_detail.html', context)


@login_required
def prompt_create(request):
    """Create a new prompt"""
    if request.method == 'POST':
        form = PromptForm(request.POST)
        if form.is_valid():
            prompt = form.save(commit=False)
            prompt.author = request.user
            prompt.save()
            messages.success(request, 'Prompt created successfully!')
            return redirect('prompt_detail', slug=prompt.slug)
    else:
        form = PromptForm()

    return render(request, 'prompts/prompt_form.html', {'form': form, 'action': 'Create', 'STATIC_VERSION': STATIC_VERSION})


@login_required
def prompt_edit(request, slug):
    """Edit an existing prompt"""
    prompt = get_object_or_404(Prompt, slug=slug, author=request.user)

    if request.method == 'POST':
        form = PromptForm(request.POST, instance=prompt)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prompt updated successfully!')
            return redirect('prompt_detail', slug=prompt.slug)
    else:
        form = PromptForm(instance=prompt)

    return render(request, 'prompts/prompt_form.html', {'form': form, 'action': 'Edit', 'prompt': prompt, 'STATIC_VERSION': STATIC_VERSION})


@login_required
def prompt_delete(request, slug):
    """Delete a prompt"""
    prompt = get_object_or_404(Prompt, slug=slug, author=request.user)

    if request.method == 'POST':
        prompt.delete()
        messages.success(request, 'Prompt deleted successfully!')
        return redirect('home')

    return render(request, 'prompts/prompt_confirm_delete.html', {'prompt': prompt, 'STATIC_VERSION': STATIC_VERSION})


@login_required
@require_POST
def prompt_upvote(request, slug):
    """Toggle upvote on a prompt"""
    prompt = get_object_or_404(Prompt, slug=slug)

    if prompt.upvotes.filter(id=request.user.id).exists():
        prompt.upvotes.remove(request.user)
        upvoted = False
    else:
        prompt.upvotes.add(request.user)
        upvoted = True

    # Get fresh count
    upvote_count = prompt.upvotes.count()

    return JsonResponse({
        'upvoted': upvoted,
        'upvote_count': upvote_count
    })


@login_required
@require_POST
def prompt_favorite(request, slug):
    """Toggle favorite on a prompt"""
    prompt = get_object_or_404(Prompt, slug=slug)

    if prompt.favorites.filter(id=request.user.id).exists():
        prompt.favorites.remove(request.user)
        favorited = False
    else:
        prompt.favorites.add(request.user)
        favorited = True

    return JsonResponse({'favorited': favorited})


@login_required
def user_prompts(request):
    """User's own prompts and favorites"""
    # Get user's prompts with upvote counts
    my_prompts = request.user.prompts.select_related('domain').annotate(
        upvote_count=Count('upvotes', distinct=True)
    ).prefetch_related('comments').all()

    # Get favorite prompts with upvote counts
    favorite_prompts = request.user.favorite_prompts.select_related('author', 'domain').annotate(
        upvote_count=Count('upvotes', distinct=True)
    ).all()

    # Calculate total upvotes - Method 1: Python sum (simpler)
    total_upvotes = sum(prompt.upvote_count for prompt in my_prompts)

    # Alternative Method 2: Database aggregation (more efficient for large datasets)
    # from django.db.models import Sum
    # total_upvotes_result = request.user.prompts.annotate(
    #     upvote_count=Count('upvotes')
    # ).aggregate(total=Sum('upvote_count'))
    # total_upvotes = total_upvotes_result['total'] or 0

    context = {
        'my_prompts': my_prompts,
        'favorite_prompts': favorite_prompts,
        'total_upvotes': total_upvotes,
        'STATIC_VERSION': STATIC_VERSION,
    }
    return render(request, 'prompts/user_prompts.html', context)

