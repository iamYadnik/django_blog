
from django import forms
from .models import Comments, Subscriber
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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
        fields = ['name', 'email', 'website', 'content']

    def __init__(self, *args, **kwargs):
        super(Commentforms, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Name', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email', 'class': 'form-control'})
        self.fields['website'].widget.attrs.update({'placeholder': 'Website (optional)', 'class': 'form-control'})
        self.fields['content'].widget.attrs.update({'placeholder': 'Type your comment....', 'class': 'form-control', 'rows': 5})