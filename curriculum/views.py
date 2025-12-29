# from django.shortcuts import render, get_object_or_404
# from django.contrib.auth import get_user_model
# from django.utils import timezone
# from .models import Chapter, Lesson, Progress

# # Import exams only if the file exists and is working
# # If you haven't created exams/models.py or migrations yet, comment lines 7 and 13 out.
# from exams.models import ActiveExam 

# User = get_user_model()

# def student_dashboard(request):
#     # 1. Get 'Hot' Active Exams (Deadline in future)
#     # Filter: end_time must be greater than now (gt = greater than)
#     now = timezone.now()
#     active_exams = ActiveExam.objects.filter(end_time__gt=now).order_by('end_time')[:3]

#     # 2. Get User's Total Stars (Already in request.user, but handy context)
#     user_stars = request.user.star_points if request.user.is_authenticated else 0

#     # 3. Calculate Progress
#     total_lessons = Lesson.objects.count()
#     completed_lessons = Progress.objects.filter(student=request.user, is_completed=True).count() if request.user.is_authenticated else 0
    
#     progress_percent = 0
#     if total_lessons > 0:
#         progress_percent = int((completed_lessons / total_lessons) * 100)

#     # 4. Top Stars (Leaderboard) - Top 5 students
#     leaderboard = User.objects.filter(is_student=True).order_by('-star_points')[:5]

#     context = {
#         'active_exams': active_exams,
#         'user_stars': user_stars,
#         'progress_percent': progress_percent,
#         'completed_lessons': completed_lessons,
#         'total_lessons': total_lessons,
#         'leaderboard': leaderboard,
#     }
#     return render(request, 'classroom/dashboard.html', context)
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.translation import activate
from django.conf import settings
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

# LANGUAGE SWITCHER VIEW
def set_language_view(request, language):
    """
    Set the user's language preference and redirect back to the referring page.
    """
    if language in dict(settings.LANGUAGES):
        activate(language)
        # Set language in session so it persists
        request.session['django_language'] = language
        response = redirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        return response
    return redirect('/')

# 1. THE DASHBOARD VIEW (With Real Data from Database)
@login_required(login_url='signin')
def student_dashboard(request):
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    user = request.user
    
    # Mock Data for Active Exams (keeping as mock for now)
    active_exams = [
        {
            'title': 'Python Basics Mid-Term',
            'end_time': timezone.now() + timedelta(days=2),
            'points_worth': 50
        },
        {
            'title': 'Algorithm Challenge',
            'end_time': timezone.now() + timedelta(hours=5),
            'points_worth': 100
        },
        {
            'title': 'Debug This Code',
            'end_time': timezone.now() + timedelta(days=1),
            'points_worth': 30
        }
    ]

    # Get real user stats
    user_stars = user.star_points
    
    # Get real progress from database
    from .models import Lesson, Progress
    total_lessons = Lesson.objects.count()
    completed_lessons = Progress.objects.filter(student=user, is_completed=True).count()
    
    progress_percent = 0
    if total_lessons > 0:
        progress_percent = int((completed_lessons / total_lessons) * 100)
    
    
    # Get real leaderboard from database
    from users.models import User
    
    # Get all students ordered by star points (descending) then by first_name (ascending for alphabetical order)
    leaderboard_students = User.objects.filter(role='student').order_by('-star_points', 'first_name')[:5]
    
    # If no students, create an empty list
    leaderboard = list(leaderboard_students) if leaderboard_students.exists() else []

    context = {
        # Real User Stats
        'user_stars': user_stars,
        'progress_percent': progress_percent,
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        
        # Lists
        'active_exams': active_exams,
        'leaderboard': leaderboard,
    }
    
    return render(request, 'classroom/dashboard.html', context)

# 2. THE LESSON DETAIL VIEW (Placeholder to fix your error)
def lesson_detail(request, lesson_id):
    # We will build this later. For now, it just renders a simple text.
    return render(request, 'base.html')