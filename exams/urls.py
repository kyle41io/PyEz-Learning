from django.urls import path
from . import views

urlpatterns = [
    # Student views
    path('<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('<int:exam_id>/submit/', views.submit_exam, name='submit_exam'),
    path('<int:exam_id>/run-code/', views.run_exam_code, name='run_exam_code'),
]
