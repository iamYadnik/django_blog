from django.shortcuts import render
from .models import Post, Comments, Tag, Profile, WebsiteMeta, Subscriber, ContentGenre, ContentType, SteamGame
from .forms import Commentforms, SubscriberForm, NewUserForm, PostForm, SteamIDForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify

from django.contrib import messages
from django.utils import timezone

import requests
import os
from django.http import JsonResponse
from dotenv import load_dotenv

load_dotenv()
 

def liked_post(request):
    posts = Post.objects.filter(likes__in=[request.user.id])
    context = {'posts': posts}
    return render(request, 'app/liked_post.html', context)

STEAM_API_KEY = os.getenv('STEAM_API_KEY', 'put-steam-api-key-here')
STEAM_API_URL = "http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/"



def get_genres_by_content_type(request):
    """
    API endpoint to get genres for a specific content type
    Used for dynamic dropdown loading
    """
    content_type_id = request.GET.get('content_type')
    
    if not content_type_id:
        return JsonResponse({'genres': []})
    
    genres = ContentGenre.objects.filter(
        content_type_id=content_type_id
    ).values('id', 'name').order_by('name')
    
    return JsonResponse({
        'genres': list(genres)
    })

@login_required(login_url='account_login')
def my_profile(request):
    """User's profile page with tabs"""
    user = request.user
    bookmarked_posts = Post.objects.filter(bookmarks=request.user)
    bookmarked_posts_count = bookmarked_posts.count()
    liked_posts = Post.objects.filter(likes=request.user)
    liked_posts_count = liked_posts.count()


    context = {
        'user': user,
        'liked_posts_count': liked_posts_count,
        'bookmarked_posts_count': bookmarked_posts_count
    }
    return render(request, 'app/my_profile.html', context)


@login_required(login_url='account_login')
def recently_played(request):
    """Display recently played Steam games"""
    user = request.user
    
    # Get user's Steam ID from profile
    steam_id = user.profile.steam_id if hasattr(user, 'profile') else None
    
    # Get recently played games from database
    recently_played_games = None
    if steam_id:
        recently_played_games = SteamGame.objects.filter(user=user).order_by('-playtime_2weeks')
    
    context = {
        'steam_id': steam_id,
        'recently_played_games': recently_played_games,
        'last_sync_time': user.profile.last_sync_time if hasattr(user, 'profile') else None,
    }
    
    return render(request, 'app/recently_played.html', context)

@login_required
def content_sync(request):
    """
    Display content sync page with Steam integration
    Ensure user has profile
    """
    # Auto-create profile if it doesn't exist
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    context = {
        'profile': profile,
    }
    return render(request, 'app/content_sync.html', context)


def fetch_steam_games(steam_id):
    """
    Fetch games from Steam API with detailed error handling
    """
    STEAM_API_KEY = os.getenv('STEAM_API_KEY')
    
    steam_id = str(steam_id).strip()
    
    if not steam_id or not steam_id.isdigit():
        raise ValueError(f"❌ Invalid Steam ID: {steam_id}")

    STEAM_API_URL = "http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/"
    
    params = {
        'steamid': steam_id,
        'key': STEAM_API_KEY,
        'format': 'json',
        'include_appinfo': True
    }
    
    try:
        response = requests.get(STEAM_API_URL, params=params, timeout=10)
        
        if response.status_code == 400:
            raise ValueError("❌ Error 400: Bad Request. Invalid Steam ID format.")
            
        if response.status_code == 403:
            raise ValueError("❌ Error 403: API Key invalid or domain mismatch.")
            
        if response.status_code != 200:
            raise ValueError(f"❌ Steam API Error: {response.status_code}")
        
        data = response.json()
        games = data.get('response', {}).get('games', [])
        
        # If 0 games, it's OK - just means no recently played games
        # This can happen if:
        # 1. Profile is private (despite settings showing public)
        # 2. User hasn't played any games
        # 3. Recently played list is empty
        
        print(f"DEBUG: Fetched {len(games)} games for Steam ID {steam_id}")
        return games
        
    except requests.exceptions.RequestException as e:
        raise ValueError(f"❌ Network Error: {str(e)}")
    except Exception as e:
        raise ValueError(f"❌ Error: {str(e)}")

    
@login_required
def sync_steam(request):
    """
    Handle Steam ID submission and sync
    """
    if request.method == 'POST':
        form = SteamIDForm(request.POST, instance=request.user.profile)
        
        if form.is_valid():
            profile = form.save()
            
            try:
                games = fetch_steam_games(profile.steam_id)
                
                # Store games even if list is empty
                for game in games:
                    SteamGame.objects.update_or_create(
                        user=request.user,
                        appid=game['appid'],
                        defaults={
                            'name': game['name'],
                            'playtime_2weeks': game.get('playtime_2weeks', 0),
                            'playtime_forever': game.get('playtime_forever', 0),
                            'img_icon_url': game.get('img_icon_url', ''),
                            'img_logo_url': game.get('img_logo_url', ''),
                        }
                    )
                profile.last_sync_time = timezone.now()
                profile.save()
                # Success message (even if 0 games)
                if len(games) == 0:
                    messages.warning(
                        request,
                        '⚠ Steam account connected but no recently played games found. '
                        'This might mean your profile is private or you have no recently played games.'
                    )
                else:
                    messages.success(
                        request,
                        f'✓ Steam account connected! Found {len(games)} games.'
                    )
                
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('app:content_sync')
            except Exception as e:
                messages.error(request, f'❌ Unexpected error: {str(e)}')
                return redirect('app:content_sync')
            
            return redirect('app:content_sync')
        
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    return redirect('app:content_sync')

@login_required(login_url='account_login')
def edit_profile(request):
    """Placeholder for edit profile - to be created later"""
    messages.info(request, 'Edit profile page coming soon!')
    return redirect('my_profile')


@login_required
def create_post(request):
    """
    Create a new blog post with auto-generated slug.
    - Requires user to be logged in
    - Auto-generates slug from title
    - Handles duplicate slugs
    - Associates tags with the post
    """
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Save the post without committing to DB yet
            post = form.save(commit=False)
            
            # Set the author to current user
            post.author = request.user
            
            # Generate slug from title
            base_slug = slugify(form.cleaned_data['title'])
            slug = base_slug
            counter = 1
            
            # Check if slug already exists, if yes, append number
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            post.slug = slug
            
            # Save the post to database
            post.save()
            
            # Save tags (many-to-many relationship)
            # The form should handle this, but if it doesn't:
            form.save_m2m()  # Save many-to-many relationships
            
            # Redirect to the newly created post
            return redirect('app:post_page', slug=post.slug)
    
    else:
        # GET request - show empty form
        form = PostForm()
    
    context = {'form': form}
    return render(request, 'app/create_post.html', context)

def all_post(request):
    posts = Post.objects.all()
    context = {'posts': posts}
    return render(request, 'app/all_posts.html', context)

def your_post(request):
    posts = Post.objects.filter(author=request.user)
    context = {'posts': posts}
    return render(request, 'app/your_post.html', context)

def all_bookmarked_post(request):
    posts = Post.objects.filter(bookmarks__in=[request.user.id])
    context = {'posts': posts}
    return render(request, 'app/all_bookmarked_post.html', context)


def like_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        post.save()
    else:
        post.likes.add(request.user)
        post.save()
    return HttpResponseRedirect(reverse('app:post_page', args=[str(slug)]))

def bookmark_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    
    if post.bookmarks.filter(id=request.user.id).exists():
        post.bookmarks.remove(request.user)
        post.save()
    else:
        post.bookmarks.add(request.user)
        post.save()
    return HttpResponseRedirect(reverse('app:post_page', args=[str(slug)]))

def register_user(request):
    form = NewUserForm()
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('app:home')
    context = {'form': form}
    return render(request, 'registration/registration.html', context)


def about(request):
    website_info = None

    if WebsiteMeta.objects.exists():
        website_info = WebsiteMeta.objects.first()

    context = {'website_info': website_info}
    return render(request, 'app/about.html', context)


def search_posts(request):
    query = ''  # Get search query safely
    results = []
    
    if request.GET.get('q'):  # Only search if query is provided
        query = request.GET.get('q')
        results = Post.objects.filter(
            title__icontains=query
        )
    
    context = {'results': results, 'query': query}
    return render(request, 'app/search.html', context)


def author_page(request, slug):
    author = Profile.objects.get(slug=slug)
    top_posts = Post.objects.filter(author__in=[author.user.id]).order_by('-view_count')[0:3]
    recent_posts = Post.objects.filter(author__in=[author.user.id]).order_by('-last_modified')[0:3]

    tags = Tag.objects.all()
    posts = Post.objects.all()
    context = {'author': author, 'author_slug': slug, 'top_posts': top_posts, 'recent_posts': recent_posts, 'tags': tags, 'posts': posts}
    return render(request, 'app/author.html', context)

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    top_posts = Post.objects.filter(tags__in=[tag.id]).order_by('-view_count')[0:3]
    recent_posts = Post.objects.filter(tags__in=[tag.id]).order_by('-last_modified')[0:3]

    tags = Tag.objects.all()
    context = {'tag': tag, 'tag_slug': slug, 'top_posts': top_posts, 'recent_posts': recent_posts, 'tags': tags}
    return render(request, 'app/tag.html', context)



def post_page(request, slug):
    post = Post.objects.get(slug=slug)
    comments = Comments.objects.filter(post=post, parent=None)


    form = Commentforms()
    #like check
    is_liked = False
    if post.likes.filter(id=request.user.id).exists():
        is_liked = True
    number_of_likes = post.number_of_likes()
    #bookmark check
    is_bookmarked = False
    if post.bookmarks.filter(id=request.user.id).exists():
        is_bookmarked = True

    # side bar
    recent_posts = Post.objects.all().exclude(id=post.id).order_by('-last_modified')[0:3]
    top_authors = User.objects.annotate(number =Count('post')).exclude(id=post.author.id).order_by('-number')[0:5]
    tags = Tag.objects.all()
    related_posts = Post.objects.filter(tags__in=post.tags.all()).exclude(id=post.id).distinct()[0:3]



    if request.POST:
        if not request.user.is_authenticated:  # ✅ NEW
            return redirect('app:account_login')
    
        comment_form = Commentforms(request.POST)
        if comment_form.is_valid():
            parent_obj = None
        
            if request.POST.get('parent'):
                parent = request.POST.get('parent')
                parent_obj = Comments.objects.get(id=parent)
        
            if parent_obj:
                comment_reply = comment_form.save(commit=False)
                comment_reply.parent = parent_obj
                comment_reply.post = post
                comment_reply.author = request.user
                comment_reply.name = request.user.first_name or request.user.username  # ✅ AUTO-FILL
                comment_reply.email = request.user.email  # ✅ AUTO-FILL
                comment_reply.save()
            else:
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.name = request.user.first_name or request.user.username  # ✅ AUTO-FILL
                comment.email = request.user.email  # ✅ AUTO-FILL
                comment.save()
        
            return HttpResponseRedirect(reverse('app:post_page', args=[slug]))

            
    if post.view_count == 0:  
        post.view_count = 1
    else:
        post.view_count += 1
    post.save()
    
    context = {'post': post, 
               'form': form, 
               'comments': comments, 
               'is_bookmarked': is_bookmarked, 
               'is_liked': is_liked, 
               'number_of_likes': number_of_likes,
               'recent_posts': recent_posts,
               'top_authors': top_authors,
               'tags': tags,
               'related_posts': related_posts,}
    return render(request, 'app/post.html', context)

def home(request):
    top_posts = Post.objects.all().order_by('-view_count')[0:3]
    recent_posts = Post.objects.all().order_by('-last_modified')[0:3]
    featured_posts = Post.objects.filter(is_featured=True)
    subscribe_form = SubscriberForm()
    
    subscribe_successful = None
    featured_post = None
    website_info = None

    if WebsiteMeta.objects.exists():
        website_info = WebsiteMeta.objects.first()

    # ✅ NEW: Handle form submission
    if featured_posts:
        featured_post = featured_posts[0]

    if request.POST and 'email' in request.POST:
        subscribe_form = SubscriberForm(request.POST)
        if subscribe_form.is_valid():
            try:
                subscribe_form.save()
                request.session['subscribed'] = True
                subscribe_successful = 'subscribed successfully'  # Save to database
                context = {
                    'top_posts': top_posts, 
                    'recent_posts': recent_posts, 
                    'subscribe_form': SubscriberForm(),  # Reset form
                    'subscribe_successful': subscribe_successful,  # Show success message
                    'featured_post': featured_post,
                    'website_info': website_info,
                }
                
                return render(request, 'app/home.html', context)
            except IntegrityError:
                # Handle duplicate email (model has unique=True)
                subscribe_form.add_error('email', 'Email already subscribed!')
    
    context = {
        'top_posts': top_posts, 
        'recent_posts': recent_posts, 
        'subscribe_form': subscribe_form,
        'featured_post': featured_post,
        'website_info': website_info,
    }
    return render(request, 'app/home.html', context)

