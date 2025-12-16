from django.contrib import admin
from .models import Post, Tag, Comments, Subscriber, Profile, WebsiteMeta

# Register your models here.
admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Comments)
admin.site.register(Profile)
admin.site.register(WebsiteMeta)
@admin.register(Subscriber)  # ← USE THIS DECORATOR
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at']  # ✅ SHOW BOTH FIELDS
    readonly_fields = ['subscribed_at']  # Auto-set, read-only
    list_filter = ['subscribed_at']  # Filter by date
    search_fields = ['email']  # Search by email
    ordering = ['-subscribed_at']