from django.contrib import admin
from .models import ContactEmail, SiteSettings, Skill, Experience, Project


# Register your models here.

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Admin interface for managing site-wide settings and content.
    Singleton pattern - only one instance exists.
    """
    
    fieldsets = (
        ('Hero Section', {
            'fields': ('welcome_message', 'welcome_subtitle', 'hero_title', 'hero_subtitle'),
            'description': 'Edit main landing page hero content'
        }),
        ('Personal Information', {
            'fields': ('name', 'brief_summary'),
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'location'),
        }),
        ('Social Links', {
            'fields': ('linkedin_link', 'github_link', 'resume_link'),
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('updated_at',)
    
    def has_add_permission(self, request):
        """Prevent creating multiple instances - singleton pattern"""
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of the settings instance"""
        return False


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """
    Admin interface for managing technical skills.
    """
    list_display = ('category', 'items_preview', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('category', 'items')
    
    fieldsets = (
        ('Skill Category', {
            'fields': ('category', 'items'),
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
        }),
    )
    
    def items_preview(self, obj):
        """Show first 50 characters of items"""
        return obj.items[:50] + '...' if len(obj.items) > 50 else obj.items
    items_preview.short_description = 'Skills Preview'


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    """
    Admin interface for managing work experience.
    """
    list_display = ('position', 'company', 'location', 'period', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'company')
    search_fields = ('position', 'company', 'location', 'achievements')
    
    fieldsets = (
        ('Position Details', {
            'fields': ('position', 'company', 'location', 'period'),
        }),
        ('Achievements', {
            'fields': ('achievements',),
            'description': 'Enter one achievement per line. Each line will be displayed as a bullet point.'
        }),
        ('Display Settings', {
            'fields': ('order', 'is_active'),
        }),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin interface for managing portfolio projects.
    """
    list_display = ('title', 'technologies_preview', 'is_featured', 'order', 'is_active')
    list_editable = ('is_featured', 'order', 'is_active')
    list_filter = ('is_featured', 'is_active')
    search_fields = ('title', 'description', 'technologies')
    
    fieldsets = (
        ('Project Information', {
            'fields': ('title', 'description', 'technologies', 'link'),
            'description': 'Enter technologies as comma-separated values (e.g., Django, Python, AWS)'
        }),
        ('Display Settings', {
            'fields': ('order', 'is_featured', 'is_active'),
        }),
    )
    
    def technologies_preview(self, obj):
        """Show first 40 characters of technologies"""
        return obj.technologies[:40] + '...' if len(obj.technologies) > 40 else obj.technologies
    technologies_preview.short_description = 'Technologies'

@admin.register(ContactEmail)
class ContactEmailAdmin(admin.ModelAdmin):
    """
    Admin interface for ContactEmail model.
    Displays and manages email submissions from portfolio visitors.
    """
    
    # Columns displayed in the list view
    list_display = ('email', 'created_at', 'formatted_date')
    
    # Add filters on the right side
    list_filter = ('created_at',)
    
    # Make fields searchable
    search_fields = ('email',)
    
    # Read-only fields (can view but not edit)
    readonly_fields = ('created_at', 'formatted_date')
    
    # Organize fields into sections
    fieldsets = (
        ('Email Information', {
            'fields': ('email',),
            'description': 'Email address submitted from the portfolio contact form'
        }),
        ('Metadata', {
            'fields': ('created_at', 'formatted_date'),
            'classes': ('collapse',),  # Collapsible section
        }),
    )
    
    # Customize ordering
    ordering = ('-created_at',)
    
    # Disable adding new entries manually (only from form submissions)
    def has_add_permission(self, request):
        """Prevent manual entry in admin - emails should come from form only"""
        return False
    
    # Custom display method for better date formatting
    def formatted_date(self, obj):
        """Display date in a more readable format"""
        return obj.created_at.strftime('%B %d, %Y at %I:%M %p')
    
    formatted_date.short_description = 'Submission Date & Time'
