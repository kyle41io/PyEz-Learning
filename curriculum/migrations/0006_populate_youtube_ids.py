# Generated manually

from django.db import migrations


def populate_youtube_ids(apps, schema_editor):
    Lesson = apps.get_model('curriculum', 'Lesson')
    
    youtube_ids = {
        1: 'WAFMOxkTLqU',
        2: 'fp_fQ8gNpNo',
        3: 'NyjwcV_at8Q',
        4: 'icU7VNHtw4E',
        5: 'iIvizLSMIbQ',
        6: '8Qaw9XNGroM',
        7: '7OMZwM_7eps',
        8: 'fPjvxxRBKUg',
        9: 'LVQwH0p7Df4',
        10: 'q8pik4BaNTM',
        11: '3Jm_pBRzN_8',
        12: 'utPUELFJyvc',
        13: 'usTZcZL-KvU',
        14: 'rmp1qMQZmtc',
        15: 'donqdiNyAq0',
        16: 'ovmFVwPKpPY',
        17: 'TFwAkHXUhm8',
    }
    
    for order, youtube_id in youtube_ids.items():
        Lesson.objects.filter(order=order).update(youtube_id=youtube_id)


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0005_remove_lesson_video_mp4_lesson_youtube_id'),
    ]

    operations = [
        migrations.RunPython(populate_youtube_ids, reverse_code=migrations.RunPython.noop),
    ]
