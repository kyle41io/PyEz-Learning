# Generated manually

from django.db import migrations
import json
import os


def populate_quiz_data(apps, schema_editor):
    Lesson = apps.get_model('curriculum', 'Lesson')
    
    # Base path to the tests directory
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'media', 'tests')
    
    # Iterate through lessons 1-17
    for lesson_order in range(1, 18):
        test_file = os.path.join(base_path, f'Test{lesson_order}.json')
        
        if os.path.exists(test_file):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    quiz_data = json.load(f)
                
                # Update the lesson with the quiz data
                Lesson.objects.filter(order=lesson_order).update(quiz_data=quiz_data)
                print(f"Populated quiz data for Lesson {lesson_order}")
            except Exception as e:
                print(f"Error loading Test{lesson_order}.json: {e}")
        else:
            print(f"Test file not found: {test_file}")


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0006_populate_youtube_ids'),
    ]

    operations = [
        migrations.RunPython(populate_quiz_data, reverse_code=migrations.RunPython.noop),
    ]
