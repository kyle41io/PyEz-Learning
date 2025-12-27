from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dashboard, name='dashboard'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('set-language/<str:language>/', views.set_language_view, name='set_language'),
]