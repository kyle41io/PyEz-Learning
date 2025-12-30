# Google OAuth Quick Setup - 2 Minutes

## Problem Fixed ✅

- ✅ Sign-in page now has proper styling (matches your app design)
- ✅ Removed hardcoded empty credentials
- ✅ Now uses database-backed OAuth configuration

## Next Step: Enable Google Login

You need to get Google OAuth credentials and add them. Takes ~2 minutes!

### Step 1: Get Google Credentials (5 min)

1. Go to: https://console.cloud.google.com/
2. Create new project or use existing
3. **Enable Google+ API**:
   - Click "Enable APIs and Services"
   - Search "Google+ API"
   - Click "Enable"
4. **Create OAuth App**:
   - Go to Credentials
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Web application"
   - Add redirect URIs:
     ```
     http://localhost:8000/accounts/google/login/callback/
     http://localhost:8000/en/accounts/google/login/callback/
     http://localhost:8000/vi/accounts/google/login/callback/
     ```
   - Click Create, copy **Client ID** and **Client Secret**

### Step 2: Run One Command (< 1 min)

```bash
python manage.py setup_google_oauth "YOUR_CLIENT_ID" "YOUR_CLIENT_SECRET"
```

Example:

```bash
python manage.py setup_google_oauth "123456789.googleusercontent.com" "GOCSPX-abc123xyz"
```

You'll see:

```
✅ Google OAuth has been successfully configured!
Site: localhost:8000
Client ID: 123456789...
```

**DONE!** 🎉

### Step 3: Test It

1. Visit: http://localhost:8000/en/signin/
2. Click "Sign in with Google"
3. Login with your Gmail account
4. Should create user and redirect to dashboard

---

## What Changed

**Before**: Sign in page tried to load Google OAuth but failed (no credentials)

**Now**:

- Sign in page is styled properly (dark mode, Tailwind CSS)
- OAuth credentials stored in database (not hardcoded in settings)
- Easy setup with management command
- Auto-extracts name, email, profile picture from Google

---

## Files Modified

1. **`templates/allauth/account/login.html`** - Custom styled login page
2. **`pyez_learning/settings.py`** - Fixed OAuth configuration
3. **`users/management/commands/setup_google_oauth.py`** - New setup command
4. **`GOOGLE_OAUTH_SETUP.md`** - Detailed documentation

---

## Verify It Works

```bash
# Check if Google OAuth is configured
python manage.py shell
from allauth.socialaccount.models import SocialApp
SocialApp.objects.filter(provider='google').exists()  # Should be True after setup
```

---

**That's it! Get your Google credentials and run the setup command.** ✨
