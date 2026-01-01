from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseForbidden
from allauth.socialaccount.models import SocialApp
from .models import User
from .forms import SignUpForm, SignInForm, CreateTeacherForm, ProfileEditForm


def home(request):
    """Home page - shows landing page for unauthenticated, dashboard for authenticated"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'auth/home.html', {'is_authenticated': False})


@require_http_methods(["GET", "POST"])
def signin(request):
    """Sign in view for existing users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Check if Google OAuth is configured
    try:
        google_app = SocialApp.objects.get(provider='google')
        has_google_oauth = True
    except SocialApp.DoesNotExist:
        has_google_oauth = False
    
    if request.method == 'POST':
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if user account is active
            if not user.is_active:
                messages.error(request, 'Your account has been deactivated. Please contact an administrator.')
                return render(request, 'auth/signin.html', {
                    'form': form,
                    'has_google_oauth': has_google_oauth
                })
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email/username or password')
    else:
        form = SignInForm()
    
    return render(request, 'auth/signin.html', {
        'form': form,
        'has_google_oauth': has_google_oauth
    })


@require_http_methods(["GET", "POST"])
def signup(request):
    """Sign up view for new users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Redirect to signin page instead of auto-login
            messages.success(request, 'Account created successfully! Please sign in.')
            return redirect('signin')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignUpForm()
    
    return render(request, 'auth/signup.html', {'form': form})


@login_required(login_url='signin')
def signout(request):
    """Sign out view"""
    logout(request)
    messages.success(request, 'You have been signed out successfully')
    return redirect('home')


def is_admin_or_superuser(user):
    """Check if user is admin or superuser"""
    return user.is_superuser or user.is_staff


@login_required(login_url='signin')
@user_passes_test(is_admin_or_superuser, login_url='dashboard')
@require_http_methods(["GET", "POST"])
def teacher_management(request):
    """Create teacher account (admin only)"""
    if request.method == 'POST':
        form = CreateTeacherForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Teacher account created for {user.first_name} {user.last_name}')
            return redirect('teacher_management')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CreateTeacherForm()
    
    context = {
        'form': form,
        'teachers': User.objects.filter(role='teacher').order_by('-created_at')
    }
    return render(request, 'auth/teacher_management.html', context)

@login_required(login_url='signin')
@user_passes_test(is_admin_or_superuser, login_url='dashboard')
def toggle_teacher_status(request, teacher_id):
    """Toggle teacher account active/inactive status (admin only)"""
    from django.http import JsonResponse
    import json
    
    if request.method == 'POST':
        try:
            teacher = User.objects.get(id=teacher_id, role='teacher')
            data = json.loads(request.body)
            teacher.is_active = data.get('is_active', True)
            teacher.save()
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Teacher not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@login_required(login_url='signin')
@require_http_methods(["GET", "POST"])
def profile(request):
    """User profile page - view and edit user information"""
    user = request.user
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            try:
                user_updated = form.save(user_instance=user, commit=True)
                # If password was changed, we need to update the session
                if form.cleaned_data.get('new_password'):
                    from django.contrib.auth import update_session_auth_hash
                    update_session_auth_hash(request, user_updated)
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            except forms.ValidationError as e:
                messages.error(request, str(e))
        else:
            # Display form errors
            for field, errors in form.errors.items():
                if field != '__all__':
                    messages.error(request, f'{field}: {errors[0]}')
    else:
        form = ProfileEditForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'auth/profile.html', context)