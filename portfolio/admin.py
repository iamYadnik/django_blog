from django.contrib import admin
from .models import ContactEmail


# Register your models here.

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
