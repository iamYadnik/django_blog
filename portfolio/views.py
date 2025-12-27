from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .models import ContactEmail
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
    
    context = {
        # Welcome Section (Dynamic)
        'welcome_message': 'Welcome to My Portfolio',
        'welcome_subtitle': 'Explore my journey as a passionate backend developer',
        
        # Basic Info
        'name': 'Yadnik Gaonkar',
        'title': 'Backend Developer Portfolio',
        'email': 'Yadnik72@gmail.com',
        'phone': '+44 7833886545',
        'location': 'Glasgow, UK',
        'linkedin_link': 'https://www.linkedin.com/in/yadnikgaonkar',
        'github_link': 'https://github.com/iamYadnik',
        'resume_link': '/path/to/resume.pdf',
        
        # Hero Section
        'hero_title': 'Backend Developer | Project Coordinator',
        'hero_subtitle': 'Python | Django | Cloud | Building scalable applications',
        
        # Technical Skills
        'skills': [
            {
                'category': 'Programming Languages',
                'items': 'Python, Java, C, HTML, SQL'
            },
            {
                'category': 'Backend & Frameworks',
                'items': 'Django ORM, Flask RESTful APIs, Django REST Framework'
            },
            {
                'category': 'Databases',
                'items': 'PostgreSQL, MySQL, MongoDB, SQLite3, MongoDB Atlas, RDS'
            },
            {
                'category': 'Cloud & DevOps',
                'items': 'AWS EC2, S3, RDS, Docker, CI/CD, PythonAnywhere, DigitalOcean'
            },
            {
                'category': 'Tools & Testing',
                'items': 'Git/GitHub, pytest, Postman, JMeter, Jira, VS Code, IntelliJ'
            },
            {
                'category': 'Data & Analytics',
                'items': 'SQL Query Optimization, Advanced Excel, Power BI, Data Analysis'
            }
        ],
        
        # Work Experience
        'experience': [
            {
                'position': 'Business Consultant',
                'company': 'Blackmont Consulting',
                'location': 'Manchester, UK',
                'period': 'Feb 2025 - Present',
                'achievements': [
                    'Conducted market trend analysis and provided strategic recommendations for business growth',
                    'Developed tailored solutions for complex client challenges with timely delivery',
                    'Established primary research channels by engaging with industry contacts and competitors'
                ]
            },
            {
                'position': 'Projects Coordinator',
                'company': 'Mobius SPS',
                'location': 'Reading, UK',
                'period': 'Aug 2024 - Nov 2024',
                'achievements': [
                    'Conducted purchase ledger reconciliations with accuracy and compliance',
                    'Ensured accurate financial reporting through meticulous data reconciliation',
                    'Managed expense payments and payroll report reviews'
                ]
            },
            {
                'position': 'Operations Analyst',
                'company': 'MyConsultUK',
                'location': 'London, UK',
                'period': 'Jan 2024 - Jul 2024',
                'achievements': [
                    'Enhanced invoicing process by integrating CRM systems, saving 5+ hours daily',
                    'Analyzed financial data and prepared detailed reports using advanced Excel (SUMIFS, VLOOKUP, VBA)',
                    'Automated repetitive tasks improving team productivity'
                ]
            },
            {
                'position': 'Project Coordinator',
                'company': '3EMBED Software Technologies',
                'location': 'India',
                'period': 'Jul 2018 - Nov 2021',
                'achievements': [
                    'Defined IT strategy, roadmap, and long-term business objectives',
                    'Developed technical documentation and created prototypes with technical teams',
                    'Conducted comprehensive QA, stress testing, and experimentation for product releases',
                    'Engaged in pre-sales consultations to understand client requirements'
                ]
            }
        ],
        
        # Featured Projects
        'projects': [
            {
                'title': 'Multi-User Blogging Platform',
                'description': 'Django web application supporting multiple users, post creation, comments, and interactions. Features Django ORM, user authentication, and database optimization.',
                'technologies': ['Django', 'Python', 'SQlite', 'HTML/CSS', 'JavaScript'],
                'link': 'https://github.com/iamYadnik/django_blog'
            },
            {
                'title': 'Job Listings Platform',
                'description': 'Full-stack Django application with customized admin panel. Hosted on PythonAnywhere with AWS S3 integration for storage management and file uploads.',
                'technologies': ['Django', 'AWS S3', 'PostgreSQL', 'PythonAnywhere', 'Bootstrap'],
                'link': 'https://github.com/iamYadnik/python_django_jobapp'
            },
            {
                'title': 'Image classification API using TensorFlow in Flask',
                'description': 'REST API built in Flask for image classification using TensorFlow.',
                'technologies': ['REST API', 'Flask', 'Image recognition'],
                'link': 'https://github.com/iamYadnik/image_classification_flask'
            }
        ]  
    }
    
    return render(request, 'portfolio/portfolio_home.html', context)


@require_http_methods(["GET"])
def portfolio_projects(request):
    """Render portfolio projects page"""
    context = {
        'title': 'My Projects',
        'projects': [
            {
                'title': 'Multi-User Blogging Platform',
                'description': 'Django web application supporting multiple users, post creation, comments, and interactions. Features Django ORM, user authentication, and database optimization.',
                'technologies': ['Django', 'Python', 'PostgreSQL', 'HTML/CSS', 'JavaScript'],
                'link': 'https://github.com/iamYadnik/django_blog'
            },
            {
                'title': 'Job Listings Platform',
                'description': 'Full-stack Django application with customized admin panel. Hosted on PythonAnywhere with AWS S3 integration for storage management and file uploads.',
                'technologies': ['Django', 'AWS S3', 'PostgreSQL', 'PythonAnywhere', 'Bootstrap'],
                'link': 'https://github.com/iamYadnik/python_django_jobapp'
            },
            {
                'title': 'Image classification API using TensorFlow in Flask',
                'description': 'REST API built in Flask for image classification using TensorFlow.',
                'technologies': ['REST API', 'Flask', 'Image recognition'],
                'link': 'https://github.com/iamYadnik/image_classification_flask'
            },
            {
                'title': 'Cold Chain Logistics System',
                'description': 'Cloud-based system designed to optimize logistics and manage perishable goods distribution. Academic project focusing on system architecture and optimization.',
                'technologies': ['Cloud Services', 'System Design', 'Database Optimization'],
                'link': '#'
            }
        ]
    }
    return render(request, 'portfolio/portfolio_projects.html', context)


@require_http_methods(["GET"])
def portfolio_about(request):
    """Render portfolio about page"""
    context = {
        'name': 'Yadnik Gaonkar',
        'title': 'About Me - Backend Developer',
    }
    return render(request, 'portfolio/portfolio_about.html', context)

