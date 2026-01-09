from django.urls import path
from . import views

urlpatterns = [
    # Student views
    path('<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('<int:exam_id>/entry/', views.exam_entry, name='exam_entry'),
    path('<int:exam_id>/submit/', views.submit_exam, name='submit_exam'),
    path('<int:exam_id>/run-code/', views.run_exam_code, name='run_exam_code'),
    
    # AI conversion endpoints
    path('ai/convert-text/', views.ai_convert_text, name='ai_convert_text'),
    path('ai/convert-file/', views.ai_convert_file, name='ai_convert_file'),
    path('ai/validate-json/', views.ai_validate_json, name='ai_validate_json'),
]
