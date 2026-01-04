# Generated migration for renaming lesson fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0008_progress_code_test_passed_progress_quiz_passed_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lesson',
            old_name='youtube_id',
            new_name='video',
        ),
        migrations.RenameField(
            model_name='lesson',
            old_name='game_html_name',
            new_name='game',
        ),
        migrations.RenameField(
            model_name='lesson',
            old_name='quiz_data',
            new_name='quiz',
        ),
        migrations.RenameField(
            model_name='lesson',
            old_name='code_test_data',
            new_name='coding',
        ),
    ]
