from django.db import models
from django.conf import settings
from django.utils import timezone

class ActiveExam(models.Model):
    EXAM_TYPE_CHOICES = [
        ('multi_choice', 'Multiple Choice Test'),
        ('coding', 'Coding Test'),
    ]
    
    CLASS_CHOICES = [
        ('10A1', '10A1'), ('10A2', '10A2'), ('10A3', '10A3'), ('10C1', '10C1'), ('10C2', '10C2'), ('10C3', '10C3'), ('10C4', '10C4'), ('10C5', '10C5'), ('10D1', '10D1'), ('10D2', '10D2'), ('11A1', '11A1'), ('11A2', '11A2'), ('11A3', '11A3'), ('11C1', '11C1'), ('11C2', '11C2'), ('11C3', '11C3'), ('11C4', '11C4'), ('11C5', '11C5'), ('11D1', '11D1'), ('11D2', '11D2'), ('12A1', '12A1'), ('12A2', '12A2'), ('12A3', '12A3'), ('12C1', '12C1'), ('12C2', '12C2'), ('12C3', '12C3'), ('12C4', '12C4'), ('12C5', '12C5'), ('12D1', '12D1'), ('12D2', '12D2'),
    ]
    
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_exams')
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='multi_choice')
    questions = models.JSONField(help_text="The JSON object containing questions/problems")
    
    # Time settings
    start_time = models.DateTimeField(blank=True, null=True, help_text="When the exam becomes visible on dashboard (optional - leave blank for always visible)")
    end_time = models.DateTimeField(blank=True, null=True, help_text="When the exam disappears from dashboard (optional - leave blank for always visible)")
    duration_minutes = models.IntegerField(default=60, help_text="Duration of the exam in minutes")
    is_ended = models.BooleanField(default=False, help_text="Teacher can manually end the exam")
    
    # Points and access control
    points_value = models.IntegerField(default=50, help_text="Maximum stars for perfect score")
    allowed_classes = models.JSONField(default=list, help_text="List of class names allowed to access")
    password = models.CharField(max_length=50, blank=True, null=True, help_text="Optional password to access exam")
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.title
    
    def is_active(self):
        """Check if exam is currently active (within start and end time)"""
        # If manually ended, not active
        if self.is_ended:
            return False
        
        now = timezone.now()
        
        # If no start time, consider it started
        started = self.start_time is None or self.start_time <= now
        
        # If no end time, consider it not ended yet
        not_ended = self.end_time is None or self.end_time >= now
        
        return started and not_ended
    
    def can_student_access(self, student):
        """Check if a student can access this exam based on their class"""
        # Teachers and admins bypass class restrictions and password, but still must follow schedule
        if student.is_teacher:
            # Still need to check if exam is active (time-based)
            if not self.is_active():
                return False
            return True
        
        # If no class restrictions, all students can access
        if not self.allowed_classes:
            return True
        
        # Check if student's class is in allowed classes
        return student.student_class in self.allowed_classes

class ExamSubmission(models.Model):
    exam = models.ForeignKey(ActiveExam, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_submissions')
    answers = models.JSONField(default=dict, help_text="Student's answers")
    score = models.IntegerField(default=0, help_text="Number of correct answers")
    total_questions = models.IntegerField(default=0, help_text="Total number of questions")
    stars_earned = models.IntegerField(default=0, help_text="Stars earned based on score")
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Exam lockdown tracking
    entered_at = models.DateTimeField(null=True, blank=True, help_text="When student entered the exam")
    abandoned = models.BooleanField(default=False, help_text="True if student abandoned the exam (navigated away)")
    time_spent_seconds = models.IntegerField(default=0, help_text="Time spent on exam in seconds")
    
    class Meta:
        unique_together = ['exam', 'student']  # Each student can only submit once per exam
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title}: {self.score}/{self.total_questions}"