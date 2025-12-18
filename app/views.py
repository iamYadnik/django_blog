from django.shortcuts import render
from .models import Post, Comments, Tag, Profile, WebsiteMeta
from .forms import Commentforms, SubscriberForm, NewUserForm, PostForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify


def liked_post(request):
    posts = Post.objects.filter(likes__in=[request.user.id])
    context = {'posts': posts}
    return render(request, 'app/liked_post.html', context)


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
            return redirect('post_page', slug=post.slug)
    
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
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        post.save()
    else:
        post.likes.add(request.user)
        post.save()
    return HttpResponseRedirect(reverse('post_page', args=[str(slug)]))

def bookmark_post(request, slug):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    
    
    if post.bookmarks.filter(id=request.user.id).exists():
        post.bookmarks.remove(request.user)
        post.save()
    else:
        post.bookmarks.add(request.user)
        post.save()
    return HttpResponseRedirect(reverse('post_page', args=[str(slug)]))

def register_user(request):
    form = NewUserForm()
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
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
        comment_form = Commentforms(request.POST)
        if comment_form.is_valid():
            parent_obj = None
            if request.POST.get('parent'):
                # save the reply
                parent = request.POST.get('parent')
                parent_obj = Comments.objects.get(id=parent)
                if parent_obj:
                    comment_reply = comment_form.save(commit=False)
                    comment_reply.parent = parent_obj
                    comment_reply.post = post
                    comment_reply.author = request.user
                    comment_reply.save()
                    return HttpResponseRedirect(reverse('post_page', args=[slug]))
            else:
                comment = comment_form.save(commit=False)
                post = Post.objects.get(id=request.POST.get('post_id'))
                
                
                comment.post = post
                comment.author = request.user  
                
                
                comment.save()
            return HttpResponseRedirect(reverse('post_page', args=[slug]))
            
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

