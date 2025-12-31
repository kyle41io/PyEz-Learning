from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    
    CLASS_CHOICES = [
        ('10A1', '10A1'), ('10A2', '10A2'), ('10A3', '10A3'), ('10C1', '10C1'), ('10C2', '10C2'), ('10C3', '10C3'), ('10C4', '10C4'), ('10C5', '10C5'), ('10D1', '10D1'), ('10D2', '10D2'), ('11A1', '11A1'), ('11A2', '11A2'), ('11A3', '11A3'), ('11C1', '11C1'), ('11C2', '11C2'), ('11C3', '11C3'), ('11C4', '11C4'), ('11C5', '11C5'), ('11D1', '11D1'), ('11D2', '11D2'), ('12A1', '12A1'), ('12A2', '12A2'), ('12A3', '12A3'), ('12C1', '12C1'), ('12C2', '12C2'), ('12C3', '12C3'), ('12C4', '12C4'), ('12C5', '12C5'), ('12D1', '12D1'), ('12D2', '12D2'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    student_class = models.CharField(max_length=10, choices=CLASS_CHOICES, blank=True, null=True)
    star_points = models.IntegerField(default=0)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        """Auto-set role to admin if user is superuser or staff"""
        if self.is_superuser or self.is_staff:
            self.role = 'admin'
        super().save(*args, **kwargs)
    
    @property
    def is_teacher(self):
        """Check if user is a teacher by role"""
        return self.role == 'teacher' or self.role == 'admin'
    
    @property
    def is_student(self):
        """Check if user is a student by role"""
        return self.role == 'student'