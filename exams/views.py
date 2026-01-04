from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg
import json

from .models import ActiveExam, ExamSubmission
from users.models import User


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
def submit_exam(request, exam_id):
    """Student submits exam answers"""
    exam = get_object_or_404(ActiveExam, id=exam_id)
    
    # Check if already submitted
    if ExamSubmission.objects.filter(exam=exam, student=request.user).exists():
        return JsonResponse({'success': False, 'error': 'Already submitted'}, status=400)
    
    try:
        data = json.loads(request.body)
        answers = data.get('answers', {})
        
        # Calculate score based on exam type
        if exam.exam_type == 'multi_choice':
            score, total = calculate_quiz_score(exam.questions, answers)
        else:  # coding
            score, total = calculate_coding_score(exam.questions, answers)
        
        # Calculate stars earned
        stars_earned = int((score / total) * exam.points_value) if total > 0 else 0
        
        # Create submission
        submission = ExamSubmission.objects.create(
            exam=exam,
            student=request.user,
            answers=answers,
            score=score,
            total_questions=total,
            stars_earned=stars_earned
        )
        
        # Award stars to student
        request.user.star_points += stars_earned
        request.user.save()
        
        return JsonResponse({
            'success': True,
            'score': score,
            'total': total,
            'stars_earned': stars_earned,
            'percentage': int((score / total) * 100) if total > 0 else 0
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
