from django.db import models
from django.core.validators import EmailValidator

# Create your models here.

class ContactEmail(models.Model):
    """
    Simple model to capture and store email addresses from portfolio visitors.
    Stores just email and timestamp - minimal, focused approach.
    """
    
    email = models.EmailField(
        max_length=254,
        validators=[EmailValidator()],
        help_text="Visitor's email address"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the email was submitted"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Email"
        verbose_name_plural = "Contact Emails"
    
    def __str__(self):
        return f"{self.email} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
