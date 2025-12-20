from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class WebsiteMeta(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    about = models.TextField()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile when a new User is created
    """
    if created:
        Profile.objects.get_or_create(
            user=instance,
            defaults={
                'slug': slugify(instance.username),
            }
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the Profile when User is saved
    """
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        pass

class ContentType(models.Model):
    """
    Predefined content types.
    NOT user-creatable, these are fixed.
    """
    CONTENT_TYPE_CHOICES = [
        ('game', 'Game'),
        ('movie', 'Movie'),
        ('tv_show', 'TV Show'),
        ('song', 'Song'),
        ('book', 'Book'),
    ]
    
    name = models.CharField(
        max_length=20,
        choices=CONTENT_TYPE_CHOICES,
        unique=True
    )
    display_name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Material icon name (e.g., 'gamepad', 'movie', 'music_note')"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Content Type'
        verbose_name_plural = 'Content Types'
    
    def __str__(self):
        return self.display_name


class ContentGenre(models.Model):
    """
    User-creatable genres.
    Linked to a ContentType.
    Dynamically grows as users create posts.
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='genres'
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_genres'
    )
    post_count = models.IntegerField(default=0, help_text="Number of posts with this genre")
    
    class Meta:
        unique_together = ('content_type', 'slug')
        ordering = ['-post_count', 'name']
        verbose_name = 'Content Genre'
        verbose_name_plural = 'Content Genres'
        indexes = [
            models.Index(fields=['content_type', 'name']),
            models.Index(fields=['-post_count']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.content_type.display_name})"

class SteamGame(models.Model):
    """Store recently played Steam games for a user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='steam_games')
    appid = models.IntegerField()
    name = models.CharField(max_length=255)
    playtime_2weeks = models.IntegerField(default=0, help_text="Minutes played in last 2 weeks")
    playtime_forever = models.IntegerField(default=0, help_text="Total minutes played")
    img_icon_url = models.CharField(max_length=500, blank=True, null=True)
    img_logo_url = models.CharField(max_length=500, blank=True, null=True)
    last_synced = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'appid')
        ordering = ['-playtime_2weeks']

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='profiles/avatars/', blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=200)
    steam_id = models.CharField(max_length=50, blank=True, null=True, unique=True, help_text="User's Steam ID for API integration")
    last_sync_time = models.DateTimeField(blank=True, null=True, help_text="Last time Steam games were synced")
    
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
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        help_text="Type of content this post is about"
    )
    content_genre = models.ForeignKey(
        ContentGenre,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        help_text="Genre of the content"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['content_type', 'content_genre']),
        ]   

    def __str__(self):
        return self.title
    
    def number_of_likes(self):
        return self.likes.count()
    
    def number_of_comments(self):
        return self.comments.count()