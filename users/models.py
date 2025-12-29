from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
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