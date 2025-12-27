from django.db import models
from django.conf import settings

class ActiveExam(models.Model):
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    questions = models.JSONField() # The JSON object from Gemini
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    points_value = models.IntegerField(default=50)

    def __str__(self):
        return self.title

class ExamSubmission(models.Model):
    exam = models.ForeignKey(ActiveExam, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)