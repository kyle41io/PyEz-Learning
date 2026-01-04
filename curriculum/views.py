from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils.translation import activate
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.clickjacking import xframe_options_sameorigin
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import os
from io import BytesIO
import base64

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
    from exams.models import ActiveExam, ExamSubmission
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        user = request.user
        
        # Get real active exams based on user role
        from django.db.models import Q
        
        if user.is_teacher:
            # For teachers/admins: show all exams that are not manually ended AND within schedule
            all_not_ended = ActiveExam.objects.filter(is_ended=False).order_by('-created_at')
            
            # Filter by schedule (teachers must follow schedule)
            accessible_exams = []
            for exam in all_not_ended:
                if exam.is_active():  # This checks both schedule and is_ended
                    accessible_exams.append(exam)
            
            active_exams = accessible_exams
        else:
            # For students: filter by class and time, exclude already submitted
            submitted_exam_ids = ExamSubmission.objects.filter(student=user).values_list('exam_id', flat=True)
            
            # Get all active exams (not manually ended)
            all_active = ActiveExam.objects.filter(is_ended=False).exclude(id__in=submitted_exam_ids)
            
            # Filter by time and access
            accessible_exams = []
        for exam in all_active:
            if exam.is_active() and exam.can_student_access(user):
                accessible_exams.append(exam)
        
        active_exams = accessible_exams

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
        
        # Get teacher's exams with submission counts
        my_exams = ActiveExam.objects.filter(teacher=user).annotate(
            submission_count=Count('submissions')
        ).order_by('-created_at')[:3]
        
        # Format for template
        my_exams_formatted = []
        for exam in my_exams:
            my_exams_formatted.append({
                'title': exam.title,
                'active': exam.is_active(),
                'submissions': exam.submission_count
            })
        
        context = {
            'is_teacher': True,
            'avg_progress': avg_progress,
            'students_finished': students_finished,
            'total_students': total_students,
            'my_exams': my_exams_formatted,
            'active_exams': active_exams,
            'leaderboard': leaderboard,
        }
    else:
        # For Students: Original data
        user_stars = user.star_points or 0
        total_lessons = Lesson.objects.count()
        completed_lessons = Progress.objects.filter(student=user, is_completed=True).count()
        
        # Use progress from model (handle None)
        progress_percent = user.progress_percent if user.progress_percent is not None else 0

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
    
    except Exception as e:
        logger.error(f"Dashboard error for user {request.user.username}: {str(e)}", exc_info=True)
        from django.http import HttpResponse
        return HttpResponse(f"<h1>Dashboard Error</h1><p>Error: {str(e)}</p><p>Please contact support.</p>", status=500)

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
                # Update student's overall progress
                request.user.update_progress()
            
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
def lesson_detail_category(request, lesson_order, category):
    from .models import Lesson, Progress
    from django.shortcuts import get_object_or_404
    
    lesson = get_object_or_404(Lesson, order=lesson_order)
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
            # Update student's overall progress
            user.update_progress()
        
        # Check if lesson is locked
        if not progress.is_unlocked:
            messages.warning(request, 'This lesson is locked. Complete previous lessons to unlock it.')
            return redirect('curriculum')
    
    # Define all possible categories in order
    category_order = ['pdf_file', 'video', 'quiz', 'coding', 'game']
    category_names = {
        'pdf_file': 'Document',
        'video': 'Video Lecture',
        'quiz': 'Quiz Test',
        'coding': 'Coding Challenge',
        'game': 'Interactive Game'
    }
    
    # Get all lessons ordered
    all_lessons = list(Lesson.objects.all().order_by('order'))
    
    # Find current lesson index
    current_lesson_index = next((i for i, l in enumerate(all_lessons) if l.id == lesson.id), None)
    
    # Get available categories for current lesson
    current_categories = []
    for cat in category_order:
        value = getattr(lesson, cat, None)
        if cat in ['quiz', 'coding']:
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
            if cat in ['quiz', 'coding']:
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
            if cat in ['quiz', 'coding']:
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
    
    # Get classmates data with progress from model
    classmates_data = []
    
    for classmate in classmates:
        classmates_data.append({
            'id': classmate.id,
            'first_name': classmate.first_name,
            'last_name': classmate.last_name,
            'username': classmate.username,
            'email': classmate.email,
            'star_points': classmate.star_points,
            'progress_percent': classmate.progress_percent,
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
    
    # Get students data with progress from model
    students_data = []
    
    for student in students:
        students_data.append({
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'username': student.username,
            'email': student.email,
            'star_points': student.star_points,
            'progress_percent': student.progress_percent,
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
        quiz_data = lesson.quiz
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
        
        # Track if quiz was already passed before this submission
        was_quiz_passed_before = progress.quiz_passed
        
        progress.quiz_score = correct_count
        progress.quiz_passed = all_correct
        
        # Check if lesson should be completed
        has_quiz = lesson.quiz and len(lesson.quiz) > 0
        has_code_test = lesson.coding and len(lesson.coding) > 0
        
        lesson_completed_now = False
        points_earned = 0
        
        # Award 10 points for passing quiz for the first time
        if progress.quiz_passed and not was_quiz_passed_before:
            points_earned = 10
            request.user.star_points += 10
            request.user.save()
        
        if has_quiz and has_code_test:
            # Need both quiz and code test to complete
            if progress.quiz_passed and progress.code_test_passed:
                if not progress.is_completed:
                    progress.is_completed = True
                    lesson_completed_now = True
        elif has_quiz and not has_code_test:
            # Only quiz, complete if passed
            if progress.quiz_passed:
                if not progress.is_completed:
                    progress.is_completed = True
                    lesson_completed_now = True
        elif not has_quiz and has_code_test:
            # Only coding test (shouldn't happen but handle it)
            if progress.code_test_passed:
                if not progress.is_completed:
                    progress.is_completed = True
                    lesson_completed_now = True
        
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
        
        # Update student's overall progress after any changes
        request.user.update_progress()
        
        return JsonResponse({
            'success': True,
            'score': correct_count,
            'total': total_questions,
            'passed': all_correct,
            'results': results,
            'points_earned': points_earned,
            'lesson_completed': lesson_completed_now
        })
        
    except Lesson.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lesson not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# SERVE GAME VIEW
@login_required(login_url='signin')
@xframe_options_sameorigin
def serve_game(request, game_name):
    """
    Serve game HTML files with Django template rendering
    Allow embedding in iframes from same origin
    """
    from django.template import Template, Context
    from django.conf import settings
    import os
    
    # Security: Only allow specific game files
    allowed_games = ['Game1.html', 'Game2.html', 'Game3.html']
    if game_name not in allowed_games:
        return HttpResponse("Game not found", status=404)
    
    # Build path to game file
    game_path = os.path.join(settings.MEDIA_ROOT, 'games', game_name)
    
    # Check if file exists
    if not os.path.exists(game_path):
        return HttpResponse("Game file not found", status=404)
    
    # Read game file
    with open(game_path, 'r', encoding='utf-8') as f:
        game_content = f.read()
    
    # Get lesson context if available
    lesson = None
    lesson_id = request.GET.get('lesson_id')
    if lesson_id:
        try:
            from .models import Lesson
            lesson = Lesson.objects.get(id=lesson_id)
        except:
            pass
    
    # If no lesson found, try to find from referer or use default
    if not lesson:
        # For Game1 (lesson 6 or 13), Game2 (lesson 10), Game3 (lesson 17)
        if game_name == 'Game1.html':
            # Try to determine from referer or default to lesson 6
            referer = request.META.get('HTTP_REFERER', '')
            if 'lesson/13' in referer or 'lesson_id=13' in referer:
                lesson_id = 13
            else:
                lesson_id = 6
        elif game_name == 'Game2.html':
            lesson_id = 10
        elif game_name == 'Game3.html':
            lesson_id = 17
        
        if lesson_id:
            try:
                from .models import Lesson
                lesson = Lesson.objects.get(order=lesson_id)
            except:
                # Create a mock lesson object with order
                class MockLesson:
                    def __init__(self, order):
                        self.order = order
                lesson = MockLesson(lesson_id)
    
    # Render as Django template
    template = Template(game_content)
    context = Context({
        'request': request,
        'lesson': lesson,
    })
    rendered_game = template.render(context)
    
    return HttpResponse(rendered_game, content_type='text/html')


# 9. RUN CODE VIEW (Execute Python code and test against test cases)
@login_required(login_url='signin')
def run_code(request, lesson_id):
    from django.http import JsonResponse
    from .models import Lesson
    import json
    import sys
    from io import StringIO
    import traceback
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    
    if request.user.role != 'student':
        return JsonResponse({'success': False, 'error': 'Only students can run code'}, status=403)
    
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        data = json.loads(request.body)
        problem_id = data.get('problem_id')
        code = data.get('code', '')
        
        # Get coding data
        coding_data = lesson.coding
        if not coding_data:
            return JsonResponse({'success': False, 'error': 'No coding data found'}, status=404)
        
        # Find the problem
        problem = None
        for p in coding_data:
            if p['question_id'] == problem_id:
                problem = p
                break
        
        if not problem:
            return JsonResponse({'success': False, 'error': 'Problem not found'}, status=404)
        
        # Run test cases
        test_cases = problem.get('test_cases', [])
        results = []
        
        for i, test_case in enumerate(test_cases):
            test_input = test_case.get('input', '')
            expected_output = test_case.get('expected_output', '').strip()
            
            try:
                # Create StringIO objects to capture input/output
                old_stdin = sys.stdin
                old_stdout = sys.stdout
                
                sys.stdin = StringIO(test_input)
                sys.stdout = StringIO()
                
                # Create a clean namespace for execution
                exec_namespace = {}
                
                # Execute the code
                exec(code, exec_namespace)
                
                # Get the output
                actual_output = sys.stdout.getvalue().strip()
                
                # Restore stdin/stdout
                sys.stdin = old_stdin
                sys.stdout = old_stdout
                
                # Compare outputs
                passed = actual_output == expected_output
                
                results.append({
                    'passed': passed,
                    'input': test_input,
                    'expected': expected_output,
                    'actual': actual_output
                })
                
            except Exception as e:
                # Restore stdin/stdout in case of error
                sys.stdin = old_stdin
                sys.stdout = old_stdout
                
                error_msg = str(e)
                error_trace = traceback.format_exc()
                
                results.append({
                    'passed': False,
                    'input': test_input,
                    'expected': expected_output,
                    'actual': f'Error: {error_msg}'
                })
        
        return JsonResponse({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Error executing code',
            'details': str(e)
        }, status=500)


# 10. SUBMIT CODING VIEW (Submit all coding problems and unlock next lesson)
@login_required(login_url='signin')
def submit_coding(request, lesson_id):
    from django.http import JsonResponse
    from .models import Lesson, Progress
    import json
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    
    if request.user.role != 'student':
        return JsonResponse({'success': False, 'error': 'Only students can submit coding'}, status=403)
    
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        data = json.loads(request.body)
        passed_problems = set(data.get('passed_problems', []))
        
        # Get coding data
        coding_data = lesson.coding
        if not coding_data:
            return JsonResponse({'success': False, 'error': 'No coding data found'}, status=404)
        
        total_problems = len(coding_data)
        all_passed = len(passed_problems) == total_problems
        
        # Update progress
        progress, created = Progress.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )
        # Track if coding test was already passed before this submission
        was_code_passed_before = progress.code_test_passed
        
        progress.code_test_passed = all_passed
        
        # Check if lesson should be completed
        has_quiz = lesson.quiz and len(lesson.quiz) > 0
        lesson_completed_now = False
        points_earned = 0
        
        # Award 10 points for passing coding test for the first time
        if progress.code_test_passed and not was_code_passed_before:
            points_earned = 10
            request.user.star_points += 10
            request.user.save()
        
        if has_quiz and all_passed:
            # Need both quiz and code test to complete
            if progress.quiz_passed and progress.code_test_passed:
                if not progress.is_completed:
                    progress.is_completed = True
                    lesson_completed_now = True
        elif not has_quiz and all_passed:
            # Only code test, complete if passed
            if progress.code_test_passed:
                if not progress.is_completed:
                    progress.is_completed = True
                    lesson_completed_now = True
        
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
        
        # Update student's overall progress
        request.user.update_progress()
        
        return JsonResponse({
            'success': True,
            'passed': all_passed,
            'solved': len(passed_problems),
            'total': total_problems,
            'points_earned': points_earned,
            'lesson_completed': lesson_completed_now
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='signin')
def render_pdf_pages(request, lesson_id):
    """
    Convert PDF pages to images and return as JSON with base64-encoded images
    """
    try:
        from .models import Lesson
        
        lesson = Lesson.objects.get(id=lesson_id)
        
        if not lesson.pdf_file:
            return JsonResponse({
                'success': False,
                'error': 'No PDF file found for this lesson'
            }, status=404)
        
        # Get the full path to the PDF file
        pdf_path = lesson.pdf_file.path
        
        if not os.path.exists(pdf_path):
            return JsonResponse({
                'success': False,
                'error': 'PDF file does not exist on server'
            }, status=404)
        
        # Open PDF with PyMuPDF
        doc = fitz.open(pdf_path)
        pages_data = []
        
        # Convert each page to image
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Render page to image at 2x scale for better quality
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PNG bytes
            img_bytes = pix.tobytes("png")
            
            # Encode to base64
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            pages_data.append({
                'page_number': page_num + 1,
                'image': f'data:image/png;base64,{img_base64}',
                'width': pix.width,
                'height': pix.height
            })
        
        doc.close()
        
        return JsonResponse({
            'success': True,
            'total_pages': len(pages_data),
            'pages': pages_data
        })
        
    except Lesson.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Lesson not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error rendering PDF: {str(e)}'
        }, status=500)


@login_required(login_url='signin')
def teaching_content(request):
    """View for teachers to manage their exams"""
    if not request.user.is_teacher:
        return redirect('dashboard')
    
    from django.db.models import Count
    from exams.models import ActiveExam
    
    # Get all exams created by this teacher with submission counts
    exams = ActiveExam.objects.filter(teacher=request.user).annotate(
        submission_count=Count('submissions')
    ).order_by('-created_at')
    
    context = {
        'exams': exams,
    }
    return render(request, 'classroom/teaching_content.html', context)


@login_required(login_url='signin')
def create_exam_view(request):
    """Wrapper for create_exam from exams app"""
    from exams.views import create_exam
    return create_exam(request)


@login_required(login_url='signin')
def teacher_exam_results_view(request, exam_id):
    """Wrapper for teacher_exam_results from exams app"""
    from exams.views import teacher_exam_results
    return teacher_exam_results(request, exam_id)


@login_required(login_url='signin')
def end_exam_view(request, exam_id):
    """Manually end an exam"""
    if not request.user.is_teacher:
        return redirect('dashboard')
    
    from exams.models import ActiveExam
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    
    exam = get_object_or_404(ActiveExam, id=exam_id, teacher=request.user)
    exam.is_ended = True
    exam.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Exam ended successfully'})
    
    return redirect('teaching_content')
