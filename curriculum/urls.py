from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dashboard, name='dashboard'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('set-language/<str:language>/', views.set_language_view, name='set_language'),
    path('manage-students/', views.manage_students, name='manage_students'),
    path('toggle-student-status/<int:student_id>/', views.toggle_student_status, name='toggle_student_status'),
]