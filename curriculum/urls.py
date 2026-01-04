from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dashboard, name='dashboard'),
    path('curriculum/', views.curriculum_view, name='curriculum'),
    path('curriculum/<int:lesson_order>/<str:category>/', views.lesson_detail_category, name='lesson_detail_category'),
    path('lesson/<int:lesson_order>/', views.lesson_detail, name='lesson_detail'),
    path('set-language/<str:language>/', views.set_language_view, name='set_language'),
    path('my-class/', views.my_class, name='my_class'),
    path('class-management/', views.class_management, name='class_management'),
    path('class-management/<str:class_name>/', views.class_detail, name='class_detail'),
    path('toggle-student-status/<int:student_id>/', views.toggle_student_status, name='toggle_student_status'),
    path('submit-quiz/<int:lesson_id>/', views.submit_quiz, name='submit_quiz'),
    path('run-code/<int:lesson_id>/', views.run_code, name='run_code'),
    path('submit-coding/<int:lesson_id>/', views.submit_coding, name='submit_coding'),
    path('render-pdf/<int:lesson_id>/', views.render_pdf_pages, name='render_pdf_pages'),
    path('game/<str:game_name>/', views.serve_game, name='serve_game'),
    path('teaching-content/', views.teaching_content, name='teaching_content'),
    path('teaching-content/create/', views.create_exam_view, name='create_exam'),
    path('teaching-content/results/<int:exam_id>/', views.teacher_exam_results_view, name='teacher_exam_results'),
    path('teaching-content/end/<int:exam_id>/', views.end_exam_view, name='end_exam'),
]
