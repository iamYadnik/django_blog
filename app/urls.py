

from django.urls import path
from . import views

urlpatterns = [
    path('post/<str:slug>/', views.post_page, name='post_page'),
    path('tag/<str:slug>/', views.tag_page, name='tag_page'),
    path('author/<str:slug>/', views.author_page, name='author_page'),
    path('search/', views.search_posts, name='search'),
    path('bookmark_post/<str:slug>/', views.bookmark_post, name='bookmark_post'),
    path('like_post/<str:slug>/', views.like_post, name='like_post'),
    path('about/', views.about, name='about'),
    path('accounts/register/', views.register_user, name='register'),
    path('', views.home, name='home'),
    path('all_bookmarked_post/', views.all_bookmarked_post, name='all_bookmarked_post'),
    path('all_post/', views.all_post, name='all_post'),
    path('your_post/', views.your_post, name='your_post'),
    path('liked_post/', views.liked_post, name='liked_post')
]

