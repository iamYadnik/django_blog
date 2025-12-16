# 📝 Django Blog Application

A modern, full-stack blogging platform built with Django. Features user authentication, post management, comments, and an intuitive admin panel.

![Django](https://img.shields.io/badge/Django-5.2.8-darkgreen?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)

## ✨ Features

- **User Authentication**
  - User registration and login
  - Password reset via email
  - User profiles

- **Blog Management**
  - Create, edit, delete posts
  - Rich text formatting
  - Draft and publish

- **Comments & Engagement**
  - Comment on posts
  - Nested threads
  - Like functionality

- **Admin Panel**
  - Custom admin interface
  - Bulk operations
  - User management

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Django 5.2.8, Python 3.10+ |
| Database | SQLite3 (dev), PostgreSQL (prod) |
| Frontend | HTML5, CSS3, Bootstrap 5 |
| Auth | Django Built-in |
| Hosting | PythonAnywhere, AWS |

## 🚀 Quick Start

### 1. Clone Repository
git clone https://github.com/iamYadnik/django_blog.git
cd django_blog
### 2. Create Virtual Environment
python -m venv venv
source venv/bin/activate # Mac/Linux

venv\Scripts\activate # Windows

text

### 3. Install Dependencies
pip install -r requirements.txt

text

### 4. Create .env File
cp .env.example .env
Edit with your settings
text

### 5. Run Migrations
python manage.py migrate

text

### 6. Create Superuser
python manage.py createsuperuser

text

### 7. Start Server
python manage.py runserver

text

Visit `http://localhost:8000/`

## 📁 Project Structure

django_blog/
├── blogapp/ # Main project
├── app/ # Blog app
├── templates/ # HTML templates
├── media/ # User uploads
├── manage.py
├── requirements.txt

## 🔧 Environment Variables

Create `.env` with:
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_password

## 👨‍💻 Author

**Yadnik Gaonkar**
- Email: Yadnik72@gmail.com
- LinkedIn: linkedin.com/in/yadnikgaonkar
- GitHub: @iamYadnik

## 📄 License

MIT License