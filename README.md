# PyEz Learning

A Django-based e-learning platform for Python education with interactive lessons, coding challenges, quizzes, and real-time progress tracking.

## ✨ Features

-  Interactive lessons with video, PDF, and mini-games
-  In-browser Python code execution and testing
-  Quiz and coding challenges
-  Progress tracking and star points system
-  Teacher dashboard for creating exams and managing classes
-  Google OAuth authentication
-  Multi-language support (English/Vietnamese)

## Quick Setup

### Prerequisites

- Python 3.10+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kyle41io/PyEz-Learning.git
   cd PyEz-Learning
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database (optional - uses SQLite by default)
   DATABASE_URL=sqlite:///db.sqlite3
   
   # Cloudinary (for file uploads)
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   
   # Google OAuth (optional)
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data (optional)**
   ```bash
   # Add sample lessons and chapters
   python manage.py loaddata curriculum/fixtures/initial_data.json
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Main app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Project Structure

```
PyEz-Learning/
├── curriculum/          # Lessons, chapters, progress tracking
├── exams/              # Exam creation and submission
├── users/              # User authentication and profiles
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── media/              # User uploads
└── pyez_learning/      # Django project settings
```

## User Roles

- **Student**: Take lessons, complete quizzes/coding tests, track progress
- **Teacher**: Create exams, manage classes, view student results
- **Admin**: Manage teachers, full system access

## Development

### Running Tests
```bash
python manage.py test
```

### Collect Static Files
```bash
python manage.py collectstatic
```

### Create Translations
```bash
python manage.py makemessages -l vi
python manage.py compilemessages
```

## Documentation

- [Authentication Setup Guide](doc/AUTHENTICATION_GUIDE.md)
- [Google OAuth Quick Start](doc/GOOGLE_OAUTH_QUICK_START.md)
- [Translation Guide](doc/TRANSLATION_GUIDE.md)

## Tech Stack

- **Backend**: Django 5.2
- **Frontend**: HTML, CSS (Tailwind-inspired), JavaScript
- **Database**: SQLite (default) / PostgreSQL (production)
- **Storage**: Cloudinary
- **Authentication**: Django Allauth + Google OAuth

## License

This project is for educational purposes.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

Project Link: [https://github.com/kyle41io/PyEz-Learning](https://github.com/kyle41io/PyEz-Learning)

---
