from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.db.models import Count, Avg
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
import tempfile

from .models import ActiveExam, ExamSubmission
from users.models import User
from .ai_converter import get_ai_converter


@login_required
def create_exam(request):
    """Teacher creates a new exam"""
    if not request.user.is_teacher:
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title')
            exam_type = request.POST.get('exam_type')
            points_value = int(request.POST.get('points_value', 50))
            duration_minutes = int(request.POST.get('duration_minutes', 60))
            start_time = request.POST.get('start_time') or None
            end_time = request.POST.get('end_time') or None
            password = request.POST.get('password', '')
            
            # Get questions (as JSON)
            questions_json = request.POST.get('questions')
            questions = json.loads(questions_json) if questions_json else []
            
            # Get allowed classes (multiple select)
            allowed_classes = request.POST.getlist('allowed_classes')
            
            # Create the exam
            exam = ActiveExam.objects.create(
                title=title,
                teacher=request.user,
                exam_type=exam_type,
                questions=questions,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=duration_minutes,
                points_value=points_value,
                allowed_classes=allowed_classes,
                password=password if password else None
            )
            
            return JsonResponse({'success': True, 'exam_id': exam.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    # GET request - show form
    context = {
        'class_choices': User.CLASS_CHOICES,
    }
    return render(request, 'exams/create_exam.html', context)


@login_required
def exam_detail(request, exam_id):
    """Student takes an exam"""
    exam = get_object_or_404(ActiveExam, id=exam_id)
    
    # Check if exam is ended
    if exam.is_ended:
        return render(request, 'exams/exam_closed.html', {'exam': exam, 'ended_by_teacher': True})
    
    # Check if exam is active (for students only, teachers can always access)
    if not request.user.is_teacher and not exam.is_active():
        return render(request, 'exams/exam_closed.html', {'exam': exam})
    
    # Check if student can access
    if not exam.can_student_access(request.user):
        return render(request, 'exams/exam_forbidden.html', {'exam': exam})
    
    # Check if already submitted
    existing_submission = ExamSubmission.objects.filter(
        exam=exam,
        student=request.user
    ).first()
    
    if existing_submission:
        return render(request, 'exams/exam_already_submitted.html', {
            'exam': exam,
            'submission': existing_submission
        })
    
    # Handle password check (skip for teachers/admins)
    if exam.password and not request.user.is_teacher:
        if request.method == 'POST':
            entered_password = request.POST.get('password')
            if entered_password != exam.password:
                return render(request, 'exams/exam_password.html', {
                    'exam': exam,
                    'error': 'Incorrect password'
                })
        else:
            return render(request, 'exams/exam_password.html', {'exam': exam})
    
    # Show the exam
    context = {
        'exam': exam,
        'questions': exam.questions,
        'exam_type': exam.exam_type,
    }
    return render(request, 'exams/exam_detail.html', context)


@login_required
@require_POST
def exam_entry(request, exam_id):
    """Record when a student enters/starts an exam"""
    exam = get_object_or_404(ActiveExam, id=exam_id)
    
    # Check if already has a submission or entry record
    existing = ExamSubmission.objects.filter(exam=exam, student=request.user).first()
    if existing:
        return JsonResponse({'success': False, 'error': 'Already entered or submitted'}, status=400)
    
    try:
        # Create a temporary submission record to mark entry
        # This prevents re-entry even if they abandon
        submission = ExamSubmission.objects.create(
            exam=exam,
            student=request.user,
            entered_at=timezone.now(),
            answers={},
            score=0,
            total_questions=len(exam.questions),
            stars_earned=0
        )
        
        return JsonResponse({'success': True, 'message': 'Exam entry recorded'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def submit_exam(request, exam_id):
    """Student submits exam answers"""
    exam = get_object_or_404(ActiveExam, id=exam_id)
    
    try:
        data = json.loads(request.body)
        answers = data.get('answers', {})
        abandoned = data.get('abandoned', False)
        time_spent = data.get('time_spent', 0)
        
        # Get or create submission (in case entry wasn't recorded)
        submission, created = ExamSubmission.objects.get_or_create(
            exam=exam,
            student=request.user,
            defaults={
                'answers': {},
                'score': 0,
                'total_questions': len(exam.questions),
                'stars_earned': 0,
                'entered_at': timezone.now()
            }
        )
        
        # If already submitted with valid score, don't allow resubmission
        if not created and submission.score > 0:
            return JsonResponse({'success': False, 'error': 'Already submitted'}, status=400)
        
        # Calculate score based on exam type
        if exam.exam_type == 'multi_choice':
            score, total = calculate_quiz_score(exam.questions, answers)
        else:  # coding
            score, total = calculate_coding_score(exam.questions, answers)
        
        # Calculate stars earned (reduced if abandoned)
        penalty = 0.5 if abandoned else 1.0
        stars_earned = int((score / total) * exam.points_value * penalty) if total > 0 else 0
        
        # Update submission
        submission.answers = answers
        submission.score = score
        submission.total_questions = total
        submission.stars_earned = stars_earned
        submission.abandoned = abandoned
        submission.time_spent_seconds = time_spent
        submission.submitted_at = timezone.now()
        submission.save()
        
        # Award stars to student (only if not already awarded)
        if created or submission.stars_earned == 0:
            request.user.star_points += stars_earned
            request.user.save()
        
        return JsonResponse({
            'success': True,
            'score': score,
            'total': total,
            'stars_earned': stars_earned,
            'percentage': int((score / total) * 100) if total > 0 else 0,
            'abandoned': abandoned
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def run_exam_code(request, exam_id):
    """Execute student's code for an exam problem (similar to lesson coding execution)"""
    exam = get_object_or_404(ActiveExam, id=exam_id)
    
    try:
        data = json.loads(request.body)
        problem_id = data.get('problem_id')
        code = data.get('code', '')
        
        # Find the problem in exam questions
        problem = None
        for p in exam.questions:
            if p.get('id') == problem_id:
                problem = p
                break
        
        if not problem:
            return JsonResponse({'success': False, 'error': 'Problem not found'}, status=404)
        
        # Execute code with test cases
        test_cases = problem.get('test_cases', [])
        all_passed = True
        results = []
        
        # Simple code execution (you should use a safer method in production)
        import sys
        from io import StringIO
        
        for test_case in test_cases:
            try:
                # Capture output
                old_stdout = sys.stdout
                sys.stdout = StringIO()
                
                # Execute the code
                exec_globals = {}
                exec(code, exec_globals)
                
                # Get output
                output = sys.stdout.getvalue().strip()
                sys.stdout = old_stdout
                
                expected = str(test_case.get('expected', '')).strip()
                passed = output == expected
                
                if not passed:
                    all_passed = False
                
                results.append({
                    'input': test_case.get('input'),
                    'expected': expected,
                    'actual': output,
                    'passed': passed
                })
            except Exception as e:
                sys.stdout = old_stdout
                all_passed = False
                results.append({
                    'input': test_case.get('input'),
                    'error': str(e),
                    'passed': False
                })
        
        return JsonResponse({
            'success': all_passed,
            'results': results,
            'error': None if all_passed else 'Some tests failed'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



@login_required
def teacher_exam_results(request, exam_id):
    """Teacher views exam results"""
    if not request.user.is_teacher:
        return redirect('dashboard')
    
    exam = get_object_or_404(ActiveExam, id=exam_id, teacher=request.user)
    submissions = exam.submissions.select_related('student').order_by('-stars_earned', '-submitted_at')
    
    context = {
        'exam': exam,
        'submissions': submissions,
        'total_submissions': submissions.count(),
        'avg_score': submissions.aggregate(avg=Avg('score'))['avg'] or 0,
    }
    return render(request, 'exams/exam_results.html', context)


@login_required
def teacher_exams_list(request):
    """Teacher views all their exams"""
    if not request.user.is_teacher:
        return redirect('dashboard')
    
    exams = ActiveExam.objects.filter(teacher=request.user).annotate(
        submission_count=Count('submissions')
    ).order_by('-created_at')
    
    context = {
        'exams': exams,
    }
    return render(request, 'exams/teacher_exams_list.html', context)


# Helper functions
def calculate_quiz_score(questions, answers):
    """Calculate score for multiple choice quiz"""
    score = 0
    total = len(questions)
    
    for question in questions:
        question_id = str(question.get('id'))
        if question_id in answers:
            student_answer = answers[question_id]
            correct_answer = question.get('correct_answer')
            if student_answer == correct_answer:
                score += 1
    
    return score, total


def calculate_coding_score(problems, answers):
    """Calculate score for coding test (based on passed tests)"""
    score = 0
    total = len(problems)
    
    for problem in problems:
        problem_id = str(problem.get('id'))
        if problem_id in answers:
            if answers[problem_id].get('passed', False):
                score += 1
    
    return score, total


# AI-Assisted Exam Creation Views
@login_required
@require_POST
@ensure_csrf_cookie
def ai_convert_text(request):
    """Convert natural language text to exam JSON using AI"""
    if not request.user.is_teacher:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        exam_type = data.get('exam_type', 'multi_choice')
        language = data.get('language', 'vi')
        
        if not text:
            return JsonResponse({'success': False, 'error': 'Text is required'}, status=400)
        
        # Use AI converter
        converter = get_ai_converter()
        result = converter.convert_text_to_exam(text, exam_type, language)
        
        return JsonResponse(result)
    
    except Exception as e:
        error_msg = str(e)
        # Check for quota/rate limit errors
        if '429' in error_msg or 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower():
            return JsonResponse({
                'success': False, 
                'error': 'AI service is temporarily busy. Please try again in a minute or use a simpler prompt.'
            }, status=429)
        return JsonResponse({'success': False, 'error': f'AI Error: {error_msg}'}, status=500)


@login_required
@require_POST
@ensure_csrf_cookie
def ai_convert_file(request):
    """Convert uploaded file to exam JSON using AI"""
    if not request.user.is_teacher:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        uploaded_file = request.FILES.get('file')
        exam_type = request.POST.get('exam_type', 'multi_choice')
        language = request.POST.get('language', 'vi')
        
        if not uploaded_file:
            return JsonResponse({'success': False, 'error': 'File is required'}, status=400)
        
        # Check file size (max 10MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'File too large (max 10MB)'}, status=400)
        
        # Save file temporarily
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in ['.txt', '.pdf']:
            return JsonResponse({'success': False, 'error': 'Only .txt and .pdf files are supported'}, status=400)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name
        
        try:
            # Use AI converter
            converter = get_ai_converter()
            result = converter.convert_file_to_exam(tmp_file_path, exam_type, language)
            return JsonResponse(result)
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
    
    except Exception as e:
        error_msg = str(e)
        # Check for quota/rate limit errors
        if '429' in error_msg or 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower():
            return JsonResponse({
                'success': False, 
                'error': 'AI service is temporarily busy. Please try again in a minute or use a simpler file.'
            }, status=429)
        return JsonResponse({'success': False, 'error': f'AI Error: {error_msg}'}, status=500)


@login_required
@require_POST
@ensure_csrf_cookie
def ai_validate_json(request):
    """Validate and fix JSON format using AI"""
    if not request.user.is_teacher:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        json_text = data.get('json_text', '').strip()
        exam_type = data.get('exam_type', 'multi_choice')
        language = data.get('language', 'vi')
        
        if not json_text:
            return JsonResponse({'success': False, 'error': 'JSON text is required'}, status=400)
        
        # Use AI converter to validate and fix
        converter = get_ai_converter()
        result = converter.validate_and_fix_json(json_text, exam_type, language)
        
        return JsonResponse(result)
    
    except Exception as e:
        error_msg = str(e)
        # Check for quota/rate limit errors
        if '429' in error_msg or 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower():
            return JsonResponse({
                'success': False, 
                'error': 'AI service is temporarily busy. Please try again in a minute.'
            }, status=429)
        return JsonResponse({'success': False, 'error': f'AI Error: {error_msg}'}, status=500)
