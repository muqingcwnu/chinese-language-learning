from django.db import migrations

def copy_data_forward(apps, schema_editor):
    GrammarLesson = apps.get_model('main_core', 'GrammarLesson')

    # Copy GrammarLesson data
    for lesson in GrammarLesson.objects.all():
        # Only copy if the new fields are empty and old fields exist
        if not lesson.title_en and hasattr(lesson, 'title'):
            lesson.title_en = lesson.title
            lesson.title_zh = lesson.title
        if not lesson.pattern_en and hasattr(lesson, 'pattern'):
            lesson.pattern_en = lesson.pattern
            lesson.pattern_zh = lesson.pattern
        if not lesson.example_en and hasattr(lesson, 'example'):
            lesson.example_en = lesson.example
            lesson.example_zh = lesson.example
        lesson.save()

def copy_data_backward(apps, schema_editor):
    # No backward operation needed since old fields are removed
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('main_core', '0005_remove_grammarlesson_example_and_more'),
    ]

    operations = [
        migrations.RunPython(copy_data_forward, copy_data_backward),
    ] 