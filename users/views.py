from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseForbidden
from .models import User
from .forms import SignUpForm, SignInForm, CreateTeacherForm


def home(request):
    """Home page - shows login/signup for unauthenticated users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'auth/home.html')


@require_http_methods(["GET", "POST"])
def signin(request):
    """Sign in view for existing users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email/username or password')
    else:
        form = SignInForm()
    
    return render(request, 'auth/signin.html', {'form': form})


@require_http_methods(["GET", "POST"])
def signup(request):
    """Sign up view for new users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login after signup
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
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
def create_teacher(request):
    """Create teacher account (admin only)"""
    if request.method == 'POST':
        form = CreateTeacherForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Teacher account created for {user.first_name} {user.last_name}')
            return redirect('create_teacher')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CreateTeacherForm()
    
    context = {
        'form': form,
        'teachers': User.objects.filter(role='teacher')
    }
    return render(request, 'auth/create_teacher.html', context)
