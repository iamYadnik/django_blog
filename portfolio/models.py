from django.db import models
from django.core.validators import EmailValidator

# Create your models here.

class SiteSettings(models.Model):
    """
    Singleton model to store editable site content.
    Only one instance should exist.
    """
    # Hero Section
    welcome_message = models.CharField(
        max_length=200,
        default='Welcome to My Portfolio',
        help_text='Main welcome heading'
    )
    welcome_subtitle = models.CharField(
        max_length=300,
        default='Explore my journey as a passionate backend developer',
        help_text='Subtitle below welcome message'
    )
    hero_title = models.CharField(
        max_length=200,
        default='Backend Developer | Project Coordinator',
        help_text='Main hero section title'
    )
    hero_subtitle = models.CharField(
        max_length=300,
        default='Python | Django | Cloud | Building scalable applications',
        help_text='Hero section subtitle'
    )
    
    # About/Bio Section
    name = models.CharField(
        max_length=100,
        default='Yadnik Gaonkar',
        help_text='Your name'
    )
    brief_summary = models.TextField(
        default='',
        blank=True,
        help_text='Brief summary about yourself'
    )
    
    # Contact Information
    email = models.EmailField(
        default='Yadnik72@gmail.com',
        help_text='Your contact email'
    )
    phone = models.CharField(
        max_length=20,
        default='+44 7833886545',
        help_text='Your phone number'
    )
    location = models.CharField(
        max_length=100,
        default='Glasgow, UK',
        help_text='Your location'
    )
    
    # Social Links
    linkedin_link = models.URLField(
        default='https://www.linkedin.com/in/yadnikgaonkar',
        help_text='LinkedIn profile URL'
    )
    github_link = models.URLField(
        default='https://github.com/iamYadnik',
        help_text='GitHub profile URL'
    )
    resume_link = models.URLField(
        default='/path/to/resume.pdf',
        blank=True,
        help_text='Resume/CV file URL'
    )
    
    # Meta
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"
    
    def __str__(self):
        return f"Site Settings (Last updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists (Singleton pattern)"""
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        """Load the singleton instance, create if doesn't exist"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


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

class Skill(models.Model):
    """
    Technical skills organized by category.
    Each skill has a category (e.g., 'Programming Languages') and items.
    """
    category = models.CharField(
        max_length=100,
        help_text='Skill category (e.g., Programming Languages, Databases)'
    )
    items = models.TextField(
        help_text='Comma-separated list of skills (e.g., Python, Java, C)'
    )
    order = models.IntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Show/hide this skill category'
    )
    
    class Meta:
        ordering = ['order', 'category']
        verbose_name = 'Technical Skill'
        verbose_name_plural = 'Technical Skills'
    
    def __str__(self):
        return f"{self.category}"


class Experience(models.Model):
    """
    Work experience entries with position, company, and achievements.
    """
    position = models.CharField(
        max_length=200,
        help_text='Job title/position'
    )
    company = models.CharField(
        max_length=200,
        help_text='Company name'
    )
    location = models.CharField(
        max_length=100,
        help_text='City, Country'
    )
    period = models.CharField(
        max_length=100,
        help_text='Time period (e.g., Jan 2024 - Jul 2024)'
    )
    achievements = models.TextField(
        help_text='One achievement per line. Each line becomes a bullet point.'
    )
    order = models.IntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Show/hide this experience'
    )
    
    class Meta:
        ordering = ['order', '-period']
        verbose_name = 'Work Experience'
        verbose_name_plural = 'Work Experience'
    
    def __str__(self):
        return f"{self.position} at {self.company}"
    
    def get_achievements_list(self):
        """Split achievements text into list by newlines"""
        return [line.strip() for line in self.achievements.split('\n') if line.strip()]


class Project(models.Model):
    """
    Portfolio projects with title, description, and technologies.
    """
    title = models.CharField(
        max_length=200,
        help_text='Project name'
    )
    description = models.TextField(
        help_text='Project description'
    )
    technologies = models.CharField(
        max_length=500,
        help_text='Comma-separated list of technologies (e.g., Django, Python, AWS)'
    )
    link = models.URLField(
        blank=True,
        help_text='GitHub or live project URL'
    )
    order = models.IntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    is_featured = models.BooleanField(
        default=True,
        help_text='Show on homepage as featured project'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Show/hide this project'
    )
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
    
    def __str__(self):
        return self.title
    
    def get_technologies_list(self):
        """Split technologies string into list"""
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]