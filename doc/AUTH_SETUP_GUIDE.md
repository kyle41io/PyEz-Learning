# PyEz Learning - Authentication System Setup & Testing Guide

## ✅ What's Been Fixed and Implemented

### 1. **User Model Simplification**

- ✅ Removed duplicate `first_name` and `last_name` fields (Django's AbstractUser already has them)
- ✅ Removed `is_teacher` and `is_student` boolean fields
- ✅ Converted them to **@property methods** that check `role` field
- ✅ This eliminates database inconsistencies and simplifies the model

### 2. **Sign Up Flow Fixed**

- ✅ Changed from auto-login to **redirect to signin** after signup
- ✅ Shows success message: "Account created successfully! Please sign in."
- ✅ Users create account and manually sign in (prevents db lock)

### 3. **Google OAuth2 Authentication**

- ✅ Installed `django-allauth` - professional OAuth2 handler
- ✅ Installed dependencies: `cryptography`, `PyJWT`, `requests-oauthlib`
- ✅ Configured Google OAuth2 provider
- ✅ Auto-extracts: first_name, last_name, email, profile_picture
- ✅ Creates user with Student role by default
- ✅ Stores Google ID for future OAuth linking
- ✅ Auto-redirects to dashboard after Google login

### 4. **Database Integrity**

- ✅ Applied all migrations without conflicts
- ✅ Removed problematic boolean fields
- ✅ Database now uses only `role` field for access control
- ✅ No more sync issues between is_teacher/is_student and role

### 5. **Role-Based Access Control**

The system now checks user role for feature access:

```python
# In templates and views:
user.role == 'student'    # Check if student
user.role == 'teacher'    # Check if teacher
user.role == 'admin'      # Check if admin

# Properties (backward compatible):
user.is_student  # Returns True if role == 'student'
user.is_teacher  # Returns True if role == 'teacher'
```

## 🚀 Google OAuth2 Setup (Required to use Google Login)

### Step 1: Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Choose **Web Application**
6. Add authorized redirect URIs:
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://localhost:8000/en/accounts/google/login/callback/
   http://localhost:8000/vi/accounts/google/login/callback/
   https://yourdomain.com/accounts/google/login/callback/
   https://yourdomain.com/en/accounts/google/login/callback/
   https://yourdomain.com/vi/accounts/google/login/callback/
   ```
7. Copy **Client ID** and **Client Secret**

### Step 2: Configure in Django Admin

1. Sign in to `/admin/`
2. Go to **Sites** and ensure you have `localhost:8000` (or your domain)
3. Go to **Social Applications**
4. Click **Add Social Application**
   - Provider: Google
   - Name: Google OAuth
   - Client id: `<paste your Client ID>`
   - Secret key: `<paste your Client Secret>`
   - Sites: Select your site
   - Save

### Step 3: Environment Variables (Optional)

Instead of admin, you can set environment variables:

```bash
export GOOGLE_OAUTH_KEY="your-client-id"
export GOOGLE_OAUTH_SECRET="your-secret-key"
```

Then update settings.py to use them (already configured).

## 📋 Testing the Authentication System

### Test 1: Regular Sign Up & Sign In

1. **Start the server**:

   ```bash
   source venv/bin/activate
   python manage.py runserver
   ```

2. **Visit home page**: `http://localhost:8000/`

   - Should show Sign In and Sign Up buttons

3. **Test Sign Up**:

   - Click "Sign Up"
   - Fill in: email, first name, last name, password (twice)
   - Click "Create Account"
   - Should redirect to Sign In page with success message
   - **Check database**: `python manage.py dbshell`
     ```sql
     SELECT * FROM users_user;
     ```
   - New user should exist with `role = 'student'`

4. **Test Sign In**:

   - Enter credentials from signup
   - Click "Sign In"
   - Should redirect to **Dashboard**
   - Navbar should show your first name initial in user circle

5. **Test Sign Out**:
   - Click burger menu
   - Click "Sign Out" (red button)
   - Should redirect to home
   - Navbar should show Sign In/Sign Up buttons

### Test 2: Google OAuth Login

**Prerequisites**: Google OAuth credentials configured in Django Admin

1. **Visit Sign In page**: `http://localhost:8000/en/signin/`

2. **Click "Sign in with Google"**

3. **Login with your Gmail account**

4. **Expected behavior**:

   - Should auto-extract your name and profile picture
   - Should create new user with Student role
   - Should redirect to Dashboard
   - Navbar should show your first name initial

5. **Verify Google data was saved**:
   ```bash
   python manage.py shell
   ```
   ```python
   from users.models import User
   user = User.objects.get(email='your-google-email@gmail.com')
   print(user.first_name)        # Your Google first name
   print(user.last_name)         # Your Google last name
   print(user.profile_picture)   # Google profile picture URL
   print(user.google_id)         # Google account ID
   print(user.role)              # Should be 'student'
   ```

### Test 3: Teacher Account Creation (Admin Only)

1. **Log in as admin**: Use `admin/admin123` credentials

   - Or create admin via: `python manage.py createsuperuser`

2. **Go to**: `http://localhost:8000/en/create-teacher/`

3. **Fill in teacher details**:

   - Email, first name, last name, password
   - Click "Create Teacher"

4. **Verify teacher was created**:
   ```bash
   python manage.py shell
   ```
   ```python
   from users.models import User
   teacher = User.objects.get(role='teacher')
   print(teacher.is_teacher)  # Should be True
   print(teacher.is_staff)    # Might be True (admin only)
   ```

### Test 4: Role-Based Navbar Changes

1. **Log in as Student**:

   - Navbar should NOT show "Teaching Content" button

2. **Log in as Teacher**:

   - Navbar SHOULD show "Teaching Content" button

3. **Log in as Admin**:
   - Can access both admin panel and teaching content

## 🔍 Database Checks

### Check user table structure:

```bash
python manage.py dbshell
.schema users_user
```

Should show:

- `role` field (CharField)
- NO `is_teacher` field
- NO `is_student` field
- `first_name`, `last_name` from AbstractUser
- `profile_picture`, `google_id`, `bio`, `created_at`

### Check for data inconsistencies:

```python
from users.models import User

# All users should have a role
users_without_role = User.objects.filter(role__isnull=True)
print(f"Users without role: {users_without_role.count()}")

# Test role properties
user = User.objects.first()
print(f"Role: {user.role}")
print(f"Is student (property): {user.is_student}")
print(f"Is teacher (property): {user.is_teacher}")
```

## 🐛 Troubleshooting

### Problem: Sign up redirects but user not in database

**Solution**: Check form validation errors

```bash
python manage.py shell
from users.forms import SignUpForm
form = SignUpForm(data={
    'email': 'test@example.com',
    'first_name': 'Test',
    'last_name': 'User',
    'password1': 'secure123',
    'password2': 'secure123'
})
print(form.errors)
```

### Problem: Google login button not working

**Solution**:

1. Check if Google OAuth app is configured in Admin
2. Verify redirect URIs in Google Console match your Django site
3. Check browser console for JavaScript errors

### Problem: User can't access dashboard after login

**Solution**:

1. Verify user.role is not NULL
2. Check LOGIN_REDIRECT_URL setting in settings.py (should be 'dashboard')
3. Verify 'dashboard' URL name exists in urls.py

### Problem: "Teaching Content" button not showing for teachers

**Solution**:

1. Verify user.role == 'teacher' in database
2. Check base.html template for the condition
3. Ensure user properties are working:
   ```bash
   python manage.py shell
   from users.models import User
   teacher = User.objects.filter(role='teacher').first()
   print(teacher.is_teacher)  # Must be True
   ```

## 📝 Important Notes

1. **Role System**:

   - Always use `user.role` for role checking
   - `user.is_teacher` and `user.is_student` are now computed properties
   - They return True/False based on role field

2. **Google OAuth**:

   - Requires environment variables or admin configuration
   - First-time login creates new account automatically
   - Subsequent logins find existing account by email

3. **Database Migrations**:

   - Applied migration 0003 that removes is_teacher/is_student fields
   - No data loss (converted to computed properties)
   - Safe to migrate back if needed

4. **Security**:
   - CSRF tokens on all forms
   - Password hashing via Django
   - OAuth2 secure token exchange
   - Email verification optional (but recommended for production)

## ✨ What's Working Now

✅ Sign up with email validation  
✅ Sign in with email/username  
✅ Google OAuth2 login  
✅ Automatic profile picture & name extraction from Google  
✅ Role-based feature visibility  
✅ Teacher account creation (admin only)  
✅ Sign out with session cleanup  
✅ Database integrity (single role field)  
✅ Multi-language support (English/Vietnamese)  
✅ Dark mode support  
✅ Responsive design

## 🎯 Next Steps (Optional Enhancements)

- [ ] Email verification on signup
- [ ] Password reset functionality
- [ ] User profile edit page
- [ ] GitHub/Microsoft OAuth providers
- [ ] Two-factor authentication
- [ ] Student subscription to teachers
- [ ] Email notifications
