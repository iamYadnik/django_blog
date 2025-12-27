from django.contrib import admin
from .models import ContentGenre, ContentType, Post, Tag, Comments, Subscriber, Profile, WebsiteMeta

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'get_content_type', 'get_content_genre', 'created_at', 'view_count', 'is_featured']
    list_filter = ['created_at', 'is_featured', 'content_type', 'content_genre']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['slug', 'created_at', 'last_modified', 'view_count']
    filter_horizontal = ['tags', 'likes', 'bookmarks']
    
    fieldsets = (
        ('Post Information', {
            'fields': ('title', 'slug', 'author', 'content')
        }),
        ('Featured & Media', {
            'fields': ('is_featured', 'image')
        }),
        ('Content Classification', {
            'fields': ('content_type', 'content_genre'),
            'description': 'Classify this post by content type and genre for recommendations'
        }),
        ('Tags & Engagement', {
            'fields': ('tags', 'likes', 'bookmarks')
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'last_modified'),
            'classes': ('collapse',)
        }),
    )
    
    def get_content_type(self, obj):
        return obj.content_type.display_name if obj.content_type else '-'
    get_content_type.short_description = 'Content Type'
    
    def get_content_genre(self, obj):
        return obj.content_genre.name if obj.content_genre else '-'
    get_content_genre.short_description = 'Genre'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_post', 'author', 'date']
    list_filter = ['date', 'post']
    search_fields = ['content', 'name', 'email']
    readonly_fields = ['date']
    
    def get_post(self, obj):
        return obj.post.title
    get_post.short_description = 'Post'
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'slug', 'steam_id', 'last_sync_time']
    list_filter = ['last_sync_time']
    search_fields = ['user__username', 'steam_id']
    readonly_fields = ['slug', 'last_sync_time']
admin.site.register(WebsiteMeta)
  # ← USE THIS DECORATOR
@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at']
    readonly_fields = ['subscribed_at']
    list_filter = ['subscribed_at']
    search_fields = ['email']
    ordering = ['-subscribed_at']
@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'icon']
    list_filter = ['name']
    search_fields = ['name', 'display_name']
    readonly_fields = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'display_name', 'icon')
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )
    
    def has_delete_permission(self, request):
        # Don't allow deleting content types
        return False
@admin.register(ContentGenre)
class ContentGenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_content_type', 'post_count', 'created_at', 'created_by']
    list_filter = ['content_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['slug', 'created_at', 'created_by', 'post_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'content_type')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Metadata', {
            'fields': ('post_count', 'created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_content_type(self, obj):
        return obj.content_type.display_name
    get_content_type.short_description = 'Content Type'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new genre
            obj.created_by = request.user
        super().save_model(request, obj, form, change)