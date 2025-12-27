from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.portfolio_home, name='home'),
    path('projects/', views.portfolio_projects, name='projects'),
    path('about/', views.portfolio_about, name='about'),
]
