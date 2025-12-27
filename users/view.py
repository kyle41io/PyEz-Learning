def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    progress, created = Progress.objects.get_or_create(student=request.user, lesson=lesson)
    
    if not progress.is_completed:
        progress.is_completed = True
        progress.save()
        
        # Award the stars to the custom User model
        user = request.user
        user.star_points += lesson.points_value
        user.save()
        
    return redirect('dashboard')