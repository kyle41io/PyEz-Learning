# Google OAuth Setup Guide

## The Problem You're Facing

When you click "Sign in with Google", you get the error:

```
Missing required parameter: client_id
Error 400: invalid_request
```

This happens because **Google OAuth credentials are not configured in your Django database**.

## Solution: Two Methods

### Method 1: Using Management Command (Easiest) ⭐ RECOMMENDED

#### Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **Google+ API**:
   - Click "Enable APIs and Services"
   - Search for "Google+ API"
   - Click "Enable"
4. Create OAuth credentials:
   - Go to **Credentials** in the left menu
   - Click **"Create Credentials"** → **"OAuth 2.0 Client ID"**
   - Choose **"Web application"**
   - Under "Authorized redirect URIs", add:
     ```
     http://localhost:8000/accounts/google/login/callback/
     http://localhost:8000/en/accounts/google/login/callback/
     http://localhost:8000/vi/accounts/google/login/callback/
     ```
   - Click "Create"
5. Copy your **Client ID** and **Client Secret** (you'll need them next)

#### Step 2: Run the Setup Command

```bash
# Activate your virtual environment
source venv/bin/activate

# Run the setup command with your credentials
python manage.py setup_google_oauth "YOUR_CLIENT_ID" "YOUR_CLIENT_SECRET"
```

**Example:**

```bash
python manage.py setup_google_oauth "123456789-abc.googleusercontent.com" "GOCSPX-your_secret_key"
```

You should see:

```
✅ Google OAuth has been successfully configured!
Site: localhost:8000 (or your domain)
Client ID: 123456789-abc...
```

**Done!** 🎉 Google OAuth is now configured.

---

### Method 2: Using Django Admin (Alternative)

If you prefer to manually configure via the admin panel:

1. **Start the server and login to admin**:

   ```bash
   python manage.py runserver
   ```

   Visit: http://localhost:8000/admin/

2. **Navigate to Social Applications**:

   - Click **Sites** → Verify your site is `localhost:8000`
   - Go to **Social Applications** → **Add Social Application**

3. **Fill in the form**:
   - **Provider**: Google
   - **Name**: Google OAuth (or anything)
   - **Client id**: (paste your Google Client ID)
   - **Secret key**: (paste your Google Client Secret)
   - **Sites**: Select your site (localhost:8000)
   - Click **Save**

---

## Testing Google OAuth

### Test 1: Check if credentials are saved

```bash
python manage.py shell
```

```python
from allauth.socialaccount.models import SocialApp
app = SocialApp.objects.get(provider='google')
print(f"Client ID: {app.client_id}")
print(f"Secret: {app.secret}")
print(f"Sites: {list(app.sites.all())}")
```

### Test 2: Try signing in with Google

1. Start the server: `python manage.py runserver`
2. Visit: http://localhost:8000/en/signin/
3. Click "Sign in with Google"
4. **Expected flow**:
   - Redirects to Google login page
   - You login with your Gmail account
   - Google asks for permissions (profile, email)
   - Redirects back to your app
   - Creates new user account with your Google info
   - Redirects to dashboard and logs you in

---

## Troubleshooting

### ❌ Still getting "Missing required parameter: client_id"

**Solution**: Verify credentials are saved in database:

```bash
python manage.py shell
from allauth.socialaccount.models import SocialApp
print(SocialApp.objects.filter(provider='google').exists())
```

Should return `True`. If `False`, run setup command again.

### ❌ "Redirect URI mismatch" error from Google

**Solution**: Update redirect URIs in Google Cloud Console:

1. Go to Google Cloud Console → Credentials
2. Click your OAuth app
3. Add all these URIs to "Authorized redirect URIs":
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://localhost:8000/en/accounts/google/login/callback/
   http://localhost:8000/vi/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```

### ❌ "Google Sign-in is not configured yet" message on signin page

**This is OK** if credentials aren't saved yet. It will disappear after setup.

### ❌ After Google login, user not created

**Check logs**:

```bash
python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.all().values_list('email', 'first_name', 'role')
```

Verify your Google account email exists in the database.

---

## For Production Deployment

When you deploy to production:

1. **Update authorized redirect URIs** in Google Cloud Console:

   ```
   https://yourdomain.com/accounts/google/login/callback/
   https://yourdomain.com/en/accounts/google/login/callback/
   https://yourdomain.com/vi/accounts/google/login/callback/
   ```

2. **Update Django site domain**:

   ```bash
   python manage.py shell
   from django.contrib.sites.models import Site
   site = Site.objects.get_current()
   site.domain = 'yourdomain.com'
   site.name = 'PyEz Learning'
   site.save()
   ```

3. **Run setup command with production credentials**:
   ```bash
   python manage.py setup_google_oauth "YOUR_PROD_CLIENT_ID" "YOUR_PROD_SECRET"
   ```

---

## What's Working Now

✅ Custom styled Google login page (matches your app design)  
✅ Google OAuth client_id automatically loaded from database  
✅ Easy setup with management command  
✅ Auto-extracts user info (name, email, profile picture)  
✅ Creates user account on first login  
✅ Dark mode support on login pages  
✅ Multi-language support (English/Vietnamese)

---

## Quick Reference Commands

```bash
# Setup Google OAuth (MOST IMPORTANT)
python manage.py setup_google_oauth "CLIENT_ID" "CLIENT_SECRET"

# Check if configured
python manage.py shell -c "from allauth.socialaccount.models import SocialApp; print(SocialApp.objects.filter(provider='google').exists())"

# View current credentials
python manage.py shell
from allauth.socialaccount.models import SocialApp
app = SocialApp.objects.get(provider='google')
print(app.client_id, app.secret)

# Start server
python manage.py runserver
```

---

**Next Step**: Get your Google OAuth credentials and run the setup command! 🚀
