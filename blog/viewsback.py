from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model
from .models import Post

User = get_user_model()

def blog(request):
    """
    Blog archive view that displays all published posts with pagination and sorting.
    Shows all published posts ordered by publication date (newest or oldest first).
    """
    # Get all published posts
    all_published_posts = Post.objects.filter(
        is_published=True,
        published_date__lte=timezone.now()
    )
    
    # Get sort parameter (default to 'newest')
    sort = request.GET.get('sort', 'newest')
    
    # Apply sorting
    if sort == 'oldest':
        all_published_posts = all_published_posts.order_by('published_date')
    else:  # newest (default)
        all_published_posts = all_published_posts.order_by('-published_date')
    
    # Pagination for published posts
    paginator = Paginator(all_published_posts, 9)  # Show 9 posts per page
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        posts = paginator.page(paginator.num_pages)
    
    #context = {
    #    "posts": posts,
    #}
    # In your view
    context = {
        'posts': posts,  # Your paginated posts
        #'search_query': search_query,
        'available_years': [2025],  # Actual years from your posts
        'available_months': [
            (1, 'January'), (2, 'February'), (3, 'March'), 
            (4, 'April'), (5, 'May'), (6, 'June'),
            (7, 'July'), (8, 'August'), (9, 'September'),
            (10, 'October'), (11, 'November'), (12, 'December')
        ],
    }    
    
    
    return render(request, "blog/blog.html", context)


def search_posts(request):
    """
    Search view for finding posts by title or content with sorting options
    """
    search_query = request.GET.get("q", "")
    
    if search_query:
        posts_list = Post.objects.filter(
            is_published=True, 
            title__icontains=search_query
        )
    else:
        # If no search term is provided, show all posts
        posts_list = Post.objects.filter(is_published=True)
    
    # Get sort parameter (default to 'newest')
    sort = request.GET.get('sort', 'newest')
    
    # Apply sorting
    if sort == 'oldest':
        posts_list = posts_list.order_by('published_date')
    else:  # newest (default)
        posts_list = posts_list.order_by('-published_date')
    
    # Pagination
    paginator = Paginator(posts_list, 9)  # Show 9 posts per page
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        "posts": posts,
        "search_query": search_query,
    }
    return render(request, "blog/blog.html", context)


def post_page(request, slug):
    post = get_object_or_404(
        Post, 
        slug=slug, 
        published_date__lte=timezone.now(), 
        is_published=True
    )
    context = {
        "post": post,     
    }
    return render(request, "blog/post.html", context)