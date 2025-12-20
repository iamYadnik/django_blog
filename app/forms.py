
from django import forms
from .models import Comments, Subscriber, Post, Tag, ContentGenre, ContentType, Profile
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SteamIDForm(forms.ModelForm):
    """
    Form for editing Steam ID in Profile model
    Allows users to add or update their Steam ID
    """
    
    steam_id = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 76561197960434622',
            'id': 'steam_id_input',
        }),
        label='Steam ID',
        help_text='Your Steam ID is a long number found in your profile URL'
    )
    
    class Meta:
        model = Profile
        fields = ['steam_id']
    
    def clean_steam_id(self):
        """
        Validate Steam ID format
        Should be numeric only, 17 digits
        """
        steam_id = self.cleaned_data.get('steam_id')
        
        if not steam_id:
            raise forms.ValidationError(
                _("Steam ID is required.")
            )
        
        # Remove any whitespace
        steam_id = steam_id.strip()
        
        # Check if it's numeric
        if not steam_id.isdigit():
            raise forms.ValidationError(
                _("Steam ID must contain only numbers. Example: 76561197960434622")
            )
        
        # Check length (Steam IDs are typically 17 digits)
        if len(steam_id) < 10:
            raise forms.ValidationError(
                _("Steam ID appears too short. Please check your profile URL.")
            )
        
        return steam_id
    
    def save(self, commit=True):
        """
        Save the Steam ID to the profile
        """
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
        
        return instance

class PostForm(forms.ModelForm):
    """
    Form for creating/editing blog posts
    Includes content_type and content_genre with dynamic genre loading
    """
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select tags for this post (optional)"
    )
    
    # New genre field - will be populated dynamically
    content_genre_new = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create new genre (optional)',
            'help_text': 'Or select from existing genres below'
        }),
        help_text='Type a new genre name to create one'
    )
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'tags', 'is_featured', 'content_type', 'content_genre']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title',
                'required': True,
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your post content here...',
                'rows': 10,
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'content_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_content_type',
            }),
            'content_genre': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_content_genre',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Empty by default
        self.fields['content_genre'].queryset = ContentGenre.objects.none()
        
        # If editing and content_type is selected, show relevant genres
        if 'content_type' in self.data:
            try:
                content_type_id = int(self.data.get('content_type'))
                self.fields['content_genre'].queryset = ContentGenre.objects.filter(
                    content_type_id=content_type_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.content_type:
            # If editing existing post
            self.fields['content_genre'].queryset = ContentGenre.objects.filter(
                content_type=self.instance.content_type
            ).order_by('name')
    
    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        content_genre = cleaned_data.get('content_genre')
        content_genre_new = cleaned_data.get('content_genre_new')
        
        # If content_type is selected, genre must be provided somehow
        if content_type:
            if not content_genre and not content_genre_new:
                raise forms.ValidationError(
                    _("Please select an existing genre or create a new one.")
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        content_type = self.cleaned_data.get('content_type')
        content_genre_new = self.cleaned_data.get('content_genre_new')
        
        # Handle new genre creation
        if content_type and content_genre_new:
            # Create new genre if it doesn't exist
            genre, created = ContentGenre.objects.get_or_create(
                content_type=content_type,
                slug=slugify(content_genre_new),
                defaults={
                    'name': content_genre_new,
                    'created_by': self.instance.author if hasattr(self, 'instance') else None,
                }
            )
            instance.content_genre = genre
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance

class NewUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter Username', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter Email', 'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Create password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password', 'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_("Username already exists. Please choose a different one."))
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email already registered. Please use a different email address."))
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords do not match. Please re-enter."))
        return password2

class SubscriberForm(forms.ModelForm):  # ← Use ModelForm!
    email = forms.EmailField(
        label=False,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'form-control',
            'required': True
        })
    )
    
    class Meta:
        model = Subscriber
        fields = ['email']


class Commentforms(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['content']  # ✅ Only content field!
    
    def __init__(self, *args, **kwargs):
        super(Commentforms, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'placeholder': 'Type your comment....',
            'class': 'form-control',
            'rows': 3
        })
