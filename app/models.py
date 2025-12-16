from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
# Create your models here.


class WebsiteMeta(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    about = models.TextField()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='profiles/avatars/', blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=200)
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.user.username)
        return super(Profile, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.user.username



class Subscriber(models.Model):
    email = models.EmailField(unique=True, max_length=100)
    subscribed_at = models.DateTimeField(auto_now_add=True)

class Comments(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, blank=True, null=True, related_name='replies')


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=100,blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=100)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        return super(Tag, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Post(models.Model):

    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, max_length=200)
    image = models.ImageField(upload_to='posts/images/', null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    view_count = models.PositiveIntegerField(default=0, null=True)
    is_featured = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    bookmarks = models.ManyToManyField(User, related_name='bookmarks', blank=True, default=None)
    likes = models.ManyToManyField(User, related_name='likes', blank=True, default=None)   

    def __str__(self):
        return self.title
    
    def number_of_likes(self):
        return self.likes.count()