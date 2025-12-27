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

# 1. THE DASHBOARD VIEW (With Mock Data)
def student_dashboard(request):
    # Mock Data for Active Exams
    active_exams = [
        {
            'title': 'Python Basics Mid-Term',
            'end_time': datetime.now() + timedelta(days=2),
            'points_worth': 50
        },
        {
            'title': 'Algorithm Challenge',
            'end_time': datetime.now() + timedelta(hours=5),
            'points_worth': 100
        },
        {
            'title': 'Debug This Code',
            'end_time': datetime.now() + timedelta(days=1),
            'points_worth': 30
        }
    ]

    # Mock Data for Leaderboard
    leaderboard = [
        {'username': 'Alex', 'star_points': 1250},
        {'username': 'Sarah', 'star_points': 980},
        {'username': 'Mike', 'star_points': 850},
        {'username': 'Emily', 'star_points': 720},
        {'username': 'John', 'star_points': 600},
    ]

    context = {
        # Fake User Stats
        'user_stars': 450, 
        'progress_percent': 65,
        'completed_lessons': 13,
        'total_lessons': 20,
        
        # Fake Lists
        'active_exams': active_exams,
        'leaderboard': leaderboard,
    }
    
    return render(request, 'classroom/dashboard.html', context)

# 2. THE LESSON DETAIL VIEW (Placeholder to fix your error)
def lesson_detail(request, lesson_id):
    # We will build this later. For now, it just renders a simple text.
    return render(request, 'base.html')