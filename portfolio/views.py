from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .models import ContactEmail, SiteSettings, Skill, Experience, Project
from django.contrib import messages

@require_http_methods(["GET", "POST"])
def portfolio_home(request):
    """Render portfolio home page with dynamic content from context"""
    if request.method == 'POST' and 'email' in request.POST:
        email = request.POST.get('email', '').strip()
    
        if email:
            try:
            # Save to database
                ContactEmail.objects.create(email=email)
                messages.success(request, '✅ Thanks! I\'ll get back to you soon!')
            except Exception as e:
                messages.error(request, '⚠️ Email already submitted. Try another!')
        else:
            messages.error(request, '❌ Please enter a valid email.')
    
    settings = SiteSettings.load()
    
    # Fetch skills, experience, and projects (only active items)
    skills = Skill.objects.filter(is_active=True)
    experience = Experience.objects.filter(is_active=True)
    projects = Project.objects.filter(is_active=True, is_featured=True)
    
    # Convert to list format for template
    skills_list = [
        {
            'category': skill.category,
            'items': skill.items
        }
        for skill in skills
    ]
    
    experience_list = [
        {
            'position': exp.position,
            'company': exp.company,
            'location': exp.location,
            'period': exp.period,
            'achievements': exp.get_achievements_list()
        }
        for exp in experience
    ]
    
    projects_list = [
        {
            'title': project.title,
            'description': project.description,
            'technologies': project.get_technologies_list(),
            'link': project.link
        }
        for project in projects
    ]

    context = {
        # Dynamic settings from database
        'welcome_message': settings.welcome_message,
        'welcome_subtitle': settings.welcome_subtitle,
        'name': settings.name,
        'title': 'Backend Developer Portfolio',
        'email': settings.email,
        'phone': settings.phone,
        'location': settings.location,
        'linkedin_link': settings.linkedin_link,
        'github_link': settings.github_link,
        'resume_link': settings.resume_link,
        'hero_title': settings.hero_title,
        'hero_subtitle': settings.hero_subtitle,
        'brief_summary': settings.brief_summary,
        
        'skills': skills_list,
        'experience': experience_list,
        'projects': projects_list,

    }
    
    return render(request, 'portfolio/portfolio_home.html', context)


@require_http_methods(["GET"])
def portfolio_projects(request):
    """Render portfolio projects page with all projects"""
    
    # Fetch all active projects (not just featured)
    projects = Project.objects.filter(is_active=True)
    
    projects_list = [
        {
            'title': project.title,
            'description': project.description,
            'technologies': project.get_technologies_list(),
            'link': project.link
        }
        for project in projects
    ]
    
    context = {
        'title': 'My Projects',
        'projects': projects_list,
    }
    
    return render(request, 'portfolio/portfolio_projects.html', context)


@require_http_methods(["GET"])
def portfolio_about(request):
    """Render portfolio about page"""
    settings = SiteSettings.load()
    
    context = {
        'name': settings.name,
        'title': 'About Me - Backend Developer',
    }
    
    return render(request, 'portfolio/portfolio_about.html', context)

