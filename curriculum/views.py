from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.translation import activate
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
    from django.db.models import Count, Avg, Q
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

    from .models import Lesson, Progress
    from users.models import User
    
    # Get real leaderboard from database
    leaderboard_students = User.objects.filter(role='student').order_by('-star_points', 'first_name')[:5]
    leaderboard = list(leaderboard_students) if leaderboard_students.exists() else []
    
    # For Teachers: Different data
    if user.is_teacher:
        total_lessons = Lesson.objects.count()
        
        # Get all students
        students = User.objects.filter(role='student')
        total_students = students.count()
        
        # Calculate average progress
        student_progress = []
        students_finished = 0
        
        for student in students:
            completed = Progress.objects.filter(student=student, is_completed=True).count()
            if total_lessons > 0:
                percent = int((completed / total_lessons) * 100)
                student_progress.append(percent)
                if percent == 100:
                    students_finished += 1
        
        avg_progress = int(sum(student_progress) / len(student_progress)) if student_progress else 0
        
        # Mock teacher exams data
        my_exams = [
            {'title': 'Python Basics Quiz', 'active': True, 'submissions': 15},
            {'title': 'Algorithm Test', 'active': True, 'submissions': 8},
            {'title': 'Final Exam', 'active': False, 'submissions': 20},
        ]
        
        context = {
            'is_teacher': True,
            'avg_progress': avg_progress,
            'students_finished': students_finished,
            'total_students': total_students,
            'my_exams': my_exams,
            'active_exams': active_exams,
            'leaderboard': leaderboard,
        }
    else:
        # For Students: Original data
        user_stars = user.star_points
        total_lessons = Lesson.objects.count()
        completed_lessons = Progress.objects.filter(student=user, is_completed=True).count()
        
        progress_percent = 0
        if total_lessons > 0:
            progress_percent = int((completed_lessons / total_lessons) * 100)

        context = {
            'is_teacher': False,
            'user_stars': user_stars,
            'progress_percent': progress_percent,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons,
            'active_exams': active_exams,
            'leaderboard': leaderboard,
        }
    
    return render(request, 'classroom/dashboard.html', context)

# 2. THE LESSON DETAIL VIEW (Placeholder to fix your error)
def lesson_detail(request, lesson_id):
    # We will build this later. For now, it just renders a simple text.
    return render(request, 'base.html')

# 3. MANAGE STUDENTS VIEW - Removed (replaced by class_management and class_detail)

# 4. TOGGLE STUDENT STATUS (For Teachers)
@login_required(login_url='signin')
def toggle_student_status(request, student_id):
    from django.http import JsonResponse
    from users.models import User
    import json
    
    # Check if user is teacher
    if not request.user.is_teacher:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        try:
            student = User.objects.get(id=student_id, role='student')
            data = json.loads(request.body)
            student.is_active = data.get('is_active', True)
            student.save()
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Student not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

# 5. CURRICULUM VIEW (Display all lessons)
@login_required(login_url='signin')
def curriculum_view(request):
    from .models import Lesson, Progress
    
    # Get all lessons ordered by order field
    lessons = Lesson.objects.all().order_by('order')
    
    # For students, add lock/unlock status
    if request.user.role == 'student':
        lessons_data = []
        for lesson in lessons:
            progress, created = Progress.objects.get_or_create(
                student=request.user,
                lesson=lesson
            )
            
            # Auto-unlock lesson 1
            if lesson.order == 1 and not progress.is_unlocked:
                progress.is_unlocked = True
                progress.save()
            
            lessons_data.append({
                'lesson': lesson,
                'progress': progress,
                'is_locked': not progress.is_unlocked
            })
        
        context = {
            'lessons_data': lessons_data,
            'is_student': True,
        }
    else:
        context = {
            'lessons': lessons,
            'is_student': False,
        }
    
    return render(request, 'classroom/curriculum.html', context)

# 6. LESSON DETAIL VIEW (Display specific category of a lesson)
@login_required(login_url='signin')
def lesson_detail_category(request, lesson_id, category):
    from .models import Lesson, Progress
    from django.shortcuts import get_object_or_404
    
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user = request.user
    
    # Check if lesson is unlocked for student
    if user.role == 'student':
        progress, created = Progress.objects.get_or_create(
            student=user,
            lesson=lesson
        )
        
        # Auto-unlock lesson 1 for all students
        if lesson.order == 1 and not progress.is_unlocked:
            progress.is_unlocked = True
            progress.save()
        
        # Check if lesson is locked
        if not progress.is_unlocked:
            messages.warning(request, 'This lesson is locked. Complete previous lessons to unlock it.')
            return redirect('curriculum')
    
    # Define all possible categories in order
    category_order = ['pdf_file', 'youtube_id', 'quiz_data', 'code_test_data', 'game_html_name']
    category_names = {
        'pdf_file': 'Document',
        'youtube_id': 'Video Lecture',
        'quiz_data': 'Quiz Test',
        'code_test_data': 'Coding Challenge',
        'game_html_name': 'Interactive Game'
    }
    
    # Get all lessons ordered
    all_lessons = list(Lesson.objects.all().order_by('order'))
    
    # Find current lesson index
    current_lesson_index = next((i for i, l in enumerate(all_lessons) if l.id == lesson.id), None)
    
    # Get available categories for current lesson
    current_categories = []
    for cat in category_order:
        value = getattr(lesson, cat, None)
        if cat in ['quiz_data', 'code_test_data']:
            if value and len(value) > 0:
                current_categories.append(cat)
        elif value:
            current_categories.append(cat)
    
    # Find current category index in current lesson
    try:
        current_category_index = current_categories.index(category)
    except ValueError:
        current_category_index = 0
        category = current_categories[0] if current_categories else None
    
    # Calculate previous category
    prev_lesson = None
    prev_category = None
    if current_category_index > 0:
        # Previous category in same lesson
        prev_lesson = lesson
        prev_category = current_categories[current_category_index - 1]
    elif current_lesson_index > 0:
        # Last category of previous lesson
        prev_lesson_obj = all_lessons[current_lesson_index - 1]
        prev_lesson_categories = []
        for cat in category_order:
            value = getattr(prev_lesson_obj, cat, None)
            if cat in ['quiz_data', 'code_test_data']:
                if value and len(value) > 0:
                    prev_lesson_categories.append(cat)
            elif value:
                prev_lesson_categories.append(cat)
        if prev_lesson_categories:
            prev_lesson = prev_lesson_obj
            prev_category = prev_lesson_categories[-1]
    
    # Calculate next category
    next_lesson = None
    next_category = None
    if current_category_index < len(current_categories) - 1:
        # Next category in same lesson
        next_lesson = lesson
        next_category = current_categories[current_category_index + 1]
    elif current_lesson_index < len(all_lessons) - 1:
        # First category of next lesson
        next_lesson_obj = all_lessons[current_lesson_index + 1]
        next_lesson_categories = []
        for cat in category_order:
            value = getattr(next_lesson_obj, cat, None)
            if cat in ['quiz_data', 'code_test_data']:
                if value and len(value) > 0:
                    next_lesson_categories.append(cat)
            elif value:
                next_lesson_categories.append(cat)
        if next_lesson_categories:
            next_lesson = next_lesson_obj
            next_category = next_lesson_categories[0]
    
    # Get category content
    category_content = getattr(lesson, category, None)
    
    # Get progress data for students
    progress_data = None
    if user.role == 'student':
        progress_data = Progress.objects.filter(student=user, lesson=lesson).first()
    
    context = {
        'lesson': lesson,
        'category': category,
        'category_name': category_names.get(category, category),
        'category_content': category_content,
        'prev_lesson': prev_lesson,
        'prev_category': prev_category,
        'next_lesson': next_lesson,
        'next_category': next_category,
        'progress': progress_data,
    }
    
    return render(request, 'classroom/lesson_detail.html', context)


# 7. MY CLASS VIEW (For Students - see classmates)
@login_required(login_url='signin')
def my_class(request):
    from django.db.models import Q
    from users.models import User
    from .models import Lesson, Progress
    
    # Check if user is student
    if request.user.role != 'student':
        return redirect('dashboard')
    
    # Check if student has a class assigned
    if not request.user.student_class:
        messages.warning(request, 'You have not been assigned to a class yet. Please update your profile.')
        return redirect('profile')
    
    # Get filter parameters
    name_filter = request.GET.get('name', '')
    progress_filter = request.GET.get('progress', '')
    stars_filter = request.GET.get('stars', '')
    
    # Get all students in the same class (including current user)
    classmates = User.objects.filter(
        role='student',
        student_class=request.user.student_class,
        is_active=True
    ).order_by('first_name', 'last_name')
    
    # Apply name filter
    if name_filter:
        classmates = classmates.filter(
            Q(first_name__icontains=name_filter) | 
            Q(last_name__icontains=name_filter) |
            Q(username__icontains=name_filter)
        )
    
    # Calculate progress for each classmate
    total_lessons = Lesson.objects.count()
    classmates_data = []
    
    for classmate in classmates:
        completed = Progress.objects.filter(student=classmate, is_completed=True).count()
        progress_percent = int((completed / total_lessons) * 100) if total_lessons > 0 else 0
        
        classmates_data.append({
            'id': classmate.id,
            'first_name': classmate.first_name,
            'last_name': classmate.last_name,
            'username': classmate.username,
            'email': classmate.email,
            'star_points': classmate.star_points,
            'progress_percent': progress_percent,
            'profile_picture': classmate.profile_picture,
            'bio': classmate.bio,
            'created_at': classmate.created_at,
            'gender': classmate.gender,
            'get_gender_display': classmate.get_gender_display() if classmate.gender else '',
        })
    
    # Apply progress filter
    if progress_filter == 'high':
        classmates_data = [c for c in classmates_data if c['progress_percent'] >= 60]
    elif progress_filter == 'low':
        classmates_data = [c for c in classmates_data if c['progress_percent'] < 60]
    
    # Apply stars filter
    if stars_filter == 'high':
        classmates_data = [c for c in classmates_data if c['star_points'] >= 30]
    elif stars_filter == 'low':
        classmates_data = [c for c in classmates_data if c['star_points'] < 30]
    
    context = {
        'classmates': classmates_data,
        'class_name': request.user.student_class,
        'total_classmates': len(classmates_data),
        'name_filter': name_filter,
        'progress_filter': progress_filter,
        'stars_filter': stars_filter,
        'progress_options': [
            ('', 'All Progress'),
            ('high', '≥ 60%'),
            ('low', '< 60%'),
        ],
        'stars_options': [
            ('', 'All Stars'),
            ('high', '≥ 30 Stars'),
            ('low', '< 30 Stars'),
        ],
    }
    
    return render(request, 'classroom/my_class.html', context)


# 8. CLASS MANAGEMENT OVERVIEW (For Teachers - see all classes)
@login_required(login_url='signin')
def class_management(request):
    from users.models import User
    from django.db.models import Count
    
    # Check if user is teacher
    if not request.user.is_teacher:
        return redirect('dashboard')
    
    # Get all classes with student counts
    classes_data = User.objects.filter(
        role='student',
        student_class__isnull=False
    ).values('student_class').annotate(
        total_students=Count('id')
    ).order_by('student_class')
    
    # Get students without a class
    no_class_count = User.objects.filter(role='student', student_class__isnull=True).count()
    
    context = {
        'classes': classes_data,
        'no_class_count': no_class_count,
    }
    
    return render(request, 'classroom/student_management.html', context)


# 9. CLASS DETAIL VIEW (For Teachers - see students in a specific class)
@login_required(login_url='signin')
def class_detail(request, class_name):
    from django.db.models import Q
    from users.models import User
    from .models import Lesson, Progress
    
    # Check if user is teacher
    if not request.user.is_teacher:
        return redirect('dashboard')
    
    # Get filter parameters
    name_filter = request.GET.get('name', '')
    progress_filter = request.GET.get('progress', '')
    stars_filter = request.GET.get('stars', '')
    class_filter = request.GET.get('class', '')
    status_filter = request.GET.get('status', '')
    
    # Get students in this class, unassigned, or all
    if class_name == 'unassigned':
        students = User.objects.filter(role='student', student_class__isnull=True)
    elif class_name == 'all':
        students = User.objects.filter(role='student')
    else:
        students = User.objects.filter(role='student', student_class=class_name)
    
    # Apply name filter
    if name_filter:
        students = students.filter(
            Q(first_name__icontains=name_filter) | 
            Q(last_name__icontains=name_filter) |
            Q(username__icontains=name_filter)
        )
    
    # Apply class filter (only for 'all' view)
    if class_name == 'all' and class_filter:
        if class_filter == 'unassigned':
            students = students.filter(student_class__isnull=True)
        else:
            students = students.filter(student_class=class_filter)
    
    # Apply status filter (only for 'all' view)
    if class_name == 'all' and status_filter:
        if status_filter == 'active':
            students = students.filter(is_active=True)
        elif status_filter == 'inactive':
            students = students.filter(is_active=False)
    
    # Calculate progress for each student
    total_lessons = Lesson.objects.count()
    students_data = []
    
    for student in students:
        completed = Progress.objects.filter(student=student, is_completed=True).count()
        progress_percent = int((completed / total_lessons) * 100) if total_lessons > 0 else 0
        
        students_data.append({
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'username': student.username,
            'email': student.email,
            'star_points': student.star_points,
            'progress_percent': progress_percent,
            'is_active': student.is_active,
            'profile_picture': student.profile_picture,
            'student_class': student.student_class,
            'bio': student.bio,
            'created_at': student.created_at,
            'gender': student.gender,
            'get_gender_display': student.get_gender_display() if student.gender else '',
        })
    
    # Apply progress filter
    if progress_filter == 'high':
        students_data = [s for s in students_data if s['progress_percent'] >= 60]
    elif progress_filter == 'low':
        students_data = [s for s in students_data if s['progress_percent'] < 60]
    
    # Apply stars filter
    if stars_filter == 'high':
        students_data = [s for s in students_data if s['star_points'] >= 30]
    elif stars_filter == 'low':
        students_data = [s for s in students_data if s['star_points'] < 30]
    
    # Get all unique classes for filter dropdown (only for 'all' view)
    all_classes = []
    class_options = []
    if class_name == 'all':
        all_classes = User.objects.filter(
            role='student', 
            student_class__isnull=False
        ).values_list('student_class', flat=True).distinct().order_by('student_class')
        class_options = [('', 'All Classes'), ('unassigned', 'Unassigned')] + [(c, c) for c in all_classes]
    
    context = {
        'students': students_data,
        'class_name': class_name,
        'name_filter': name_filter,
        'progress_filter': progress_filter,
        'stars_filter': stars_filter,
        'class_filter': class_filter,
        'status_filter': status_filter,
        'all_classes': all_classes,
        'total_students': len(students_data),
        'progress_options': [
            ('', 'All Progress'),
            ('high', '≥ 60%'),
            ('low', '< 60%'),
        ],
        'stars_options': [
            ('', 'All Stars'),
            ('high', '≥ 30 Stars'),
            ('low', '< 30 Stars'),
        ],
        'class_options': class_options,
        'status_options': [
            ('', 'All Status'),
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ],
    }
    
    return render(request, 'classroom/class_detail.html', context)


# 8. SUBMIT QUIZ VIEW (Handle quiz submission and unlock next lesson)
@login_required(login_url='signin')
def submit_quiz(request, lesson_id):
    from django.http import JsonResponse
    from .models import Lesson, Progress
    import json
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    
    if request.user.role != 'student':
        return JsonResponse({'success': False, 'error': 'Only students can submit quizzes'}, status=403)
    
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        data = json.loads(request.body)
        answers = data.get('answers', {})
        
        # Get quiz data
        quiz_data = lesson.quiz_data
        if not quiz_data:
            return JsonResponse({'success': False, 'error': 'No quiz data found'}, status=404)
        
        # Calculate score
        correct_count = 0
        total_questions = len(quiz_data)
        results = []
        
        for question in quiz_data:
            question_id = str(question['question_id'])
            user_answer = answers.get(question_id)
            correct_answer = question['answer']
            
            is_correct = str(user_answer) == str(correct_answer)
            if is_correct:
                correct_count += 1
            
            results.append({
                'question_id': question_id,
                'correct': is_correct,
                'user_answer': user_answer,
                'correct_answer': correct_answer
            })
        
        # Check if all answers are correct
        all_correct = correct_count == total_questions
        
        # Update progress
        progress, created = Progress.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )
        progress.quiz_score = correct_count
        progress.quiz_passed = all_correct
        
        # Check if lesson should be completed
        has_code_test = lesson.code_test_data and len(lesson.code_test_data) > 0
        if has_code_test:
            # Need both quiz and code test to complete
            if progress.quiz_passed and progress.code_test_passed:
                progress.is_completed = True
                # Award points
                request.user.star_points += lesson.points_value
                request.user.save()
        else:
            # Only quiz, complete if passed
            if progress.quiz_passed:
                progress.is_completed = True
                # Award points
                request.user.star_points += lesson.points_value
                request.user.save()
        
        progress.save()
        
        # Unlock next lesson if current is completed
        if progress.is_completed:
            next_lesson = Lesson.objects.filter(order=lesson.order + 1).first()
            if next_lesson:
                next_progress, _ = Progress.objects.get_or_create(
                    student=request.user,
                    lesson=next_lesson
                )
                next_progress.is_unlocked = True
                next_progress.save()
        
        return JsonResponse({
            'success': True,
            'score': correct_count,
            'total': total_questions,
            'passed': all_correct,
            'results': results,
            'lesson_completed': progress.is_completed,
            'points_earned': lesson.points_value if progress.is_completed else 0
        })
        
    except Lesson.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lesson not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
