from django import forms
from django.core.exceptions import ValidationError
from .models import ContactEmail


class ContactEmailForm(forms.ModelForm):
    """
    Simple form for capturing email addresses from portfolio visitors.
    Just email field - minimal and focused.
    """
    
    class Meta:
        model = ContactEmail
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control contact-email',
                    'placeholder': 'your.email@example.com',
                    'required': True,
                    'aria-label': 'Email Address',
                    'autocomplete': 'email',
                }
            ),
        }
        labels = {
            'email': 'Your Email Address',
        }
    
    def clean_email(self):
        """Validate email field"""
        email = self.cleaned_data.get('email')
        
        if email:
            # Check if email is valid format (basic check)
            if '@' not in email or '.' not in email:
                raise ValidationError(
                    "Please enter a valid email address.",
                    code='invalid_email'
                )
            
            # Optional: Check if email already exists
            if ContactEmail.objects.filter(email=email).exists():
                raise ValidationError(
                    "This email has already been submitted. Thanks!",
                    code='duplicate_email'
                )
        
        return email
    
    def clean(self):
        """Overall form validation"""
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        
        if email:
            # Additional validation if needed
            pass
        
        return cleaned_data
