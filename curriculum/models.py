from django.db import models
from django.conf import settings

class Chapter(models.Model):
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.order}. {self.title}"

class Lesson(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons', blank=True, null=True)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)
    points_value = models.IntegerField(default=10, help_text="Stars awarded for completing this lesson")
    # Files
    youtube_id = models.CharField(max_length=20, blank=True, null=True, help_text="YouTube video ID")
    pdf_file = models.FileField(upload_to='lessons/docs/', blank=True, null=True)
    game_html_name = models.CharField(max_length=100, blank=True, help_text="Name of game file in static")

    # Static Tests (JSON for flexibility)
    quiz_data = models.JSONField(default=list, blank=True) 
    code_test_data = models.JSONField(default=list, blank=True) 

    def __str__(self):
        return self.title
    
    @property
    def youtube_url(self):
        """Returns the full YouTube watch URL"""
        if self.youtube_id:
            return f"https://www.youtube.com/watch?v={self.youtube_id}"
        return None
    
    @property
    def youtube_embed_url(self):
        """Returns the YouTube embed URL for iframe"""
        if self.youtube_id:
            return f"https://www.youtube.com/embed/{self.youtube_id}"
        return None

class Progress(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    is_unlocked = models.BooleanField(default=False)
    quiz_passed = models.BooleanField(default=False)
    quiz_score = models.IntegerField(default=0, help_text="Number of correct answers")
    code_test_passed = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Progress"
        unique_together = ('student', 'lesson')