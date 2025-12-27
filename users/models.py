from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)
    star_points = models.IntegerField(default=0)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    profile_picture = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        # Auto-set is_teacher and is_student based on role
        self.is_teacher = (self.role == 'teacher')
        self.is_student = (self.role == 'student')
        super().save(*args, **kwargs)