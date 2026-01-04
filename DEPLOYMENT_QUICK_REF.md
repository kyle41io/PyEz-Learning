# Quick Deployment Commands

## Before Deployment
```bash
# 1. Commit all changes
git add .
git commit -m "Prepare for deployment"
git push origin main

# 2. Generate SECRET_KEY for production
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Railway.app Deployment

### Environment Variables to Set:
```
SECRET_KEY=<generated-key-from-above>
DEBUG=False
ALLOWED_HOSTS=.railway.app
```

### After First Deploy (in Railway Terminal):
```bash
python manage.py migrate
python manage.py createsuperuser
```

## Test Locally Before Deploy
```bash
# Test with production settings
export DEBUG=False
export SECRET_KEY=test-key
export ALLOWED_HOSTS=localhost,127.0.0.1

python manage.py collectstatic --noinput
python manage.py migrate
gunicorn pyez_learning.wsgi
```

## If Upgrading to PostgreSQL

### Add to requirements.txt:
```
dj-database-url==2.2.0
psycopg2-binary==2.9.10
```

### Add to settings.py (after imports):
```python
import dj_database_url

# Replace DATABASES
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600
    )
}
```

## Common Issues

**400 Bad Request** → Check ALLOWED_HOSTS  
**Static files 404** → Check WhiteNoise middleware  
**Database errors** → Run migrations  
**Data loss** → Switch from SQLite to PostgreSQL
