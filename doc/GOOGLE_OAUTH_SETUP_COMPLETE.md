# Google OAuth Setup Complete! 🎉

## What has been configured:

### 1. **Google OAuth Credentials**
   - Client ID: ''
   - Successfully configured in database

### 2. **Settings Configuration**
   - Added `prompt: 'select_account'` to force Google account selection popup
   - Configured proper scopes for profile and email
   - Set up automatic user creation with role='student'

### 3. **User Adapter**
   - Automatically downloads and saves Google profile pictures
   - Extracts first name, last name from Google account
   - Creates username from email if not provided
   - Links existing users by email address

## ⚠️ Important: Update Google Cloud Console

You MUST add these authorized redirect URIs in your Google Cloud Console:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Select your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", add:
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://localhost:8000/en/accounts/google/login/callback/
   http://localhost:8000/vi/accounts/google/login/callback/
   ```

## 🚀 How to Test:

1. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

2. **Visit the login page:**
   ```
   http://localhost:8000/en/signin/
   ```

3. **Click "Sign in with Google"** - You should see:
   - A popup window (or redirect) showing Google account selection
   - Choose your Google account
   - Grant permissions
   - Automatically redirected to dashboard

## 📝 What happens when a user signs in with Google:

1. **First time users:**
   - New account created automatically
   - First name from Google: `given_name`
   - Last name from Google: `family_name`
   - Profile picture downloaded from Google
   - Username generated from email
   - Role set to 'student'
   - Google ID saved for future logins

2. **Existing users (same email):**
   - Links Google account to existing account
   - Updates profile if information is missing

## 🔍 Troubleshooting:

### If the popup doesn't appear:
- Check browser popup blockers
- Make sure redirect URIs are correctly set in Google Cloud Console
- Clear browser cache and cookies

### If you get "redirect_uri_mismatch" error:
- Double-check the redirect URIs in Google Cloud Console
- Make sure they end with a trailing slash `/`
- Make sure the domain matches exactly (including http/https)

### If profile picture doesn't save:
- Check that `Pillow` package is installed
- Check that `MEDIA_ROOT` directory exists and is writable
- Check Django logs for any errors

## 📦 Required Packages:
All installed automatically via requirements.txt:
- Django>=5.0,<6.0
- django-allauth>=0.57.0
- Pillow>=10.0.0
- requests>=2.31.0

## ✅ Setup Verification:

Run this command to verify Google OAuth is configured:
```bash
python manage.py shell
```

Then run:
```python
from allauth.socialaccount.models import SocialApp
apps = SocialApp.objects.filter(provider='google')
print(f"Google OAuth configured: {apps.exists()}")
if apps.exists():
    app = apps.first()
    print(f"Client ID: {app.client_id}")
    print(f"Sites: {[site.domain for site in app.sites.all()]}")
```

Expected output:
```
Google OAuth configured: True
Client ID: 743270219955-ug1ggrpibguvmf92h7327gpfthr3hnrm.apps.googleusercontent.com
Sites: ['localhost:8000']
```

## 🎯 Next Steps:

1. Update Google Cloud Console redirect URIs (required!)
2. Start the server and test the login flow
3. Check that user profile pictures are being saved
4. Verify that first name and last name are being populated

Enjoy your Google OAuth integration! 🚀
