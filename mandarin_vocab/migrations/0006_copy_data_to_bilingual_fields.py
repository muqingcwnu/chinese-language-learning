from django.db import migrations

def copy_data_forward(apps, schema_editor):
    HSKBook = apps.get_model('mandarin_vocab', 'HSKBook')
    BookChapter = apps.get_model('mandarin_vocab', 'BookChapter')

    # Copy HSKBook data
    for book in HSKBook.objects.all():
        # Only copy if the new fields are empty and old fields exist
        if not book.title_en and hasattr(book, 'title'):
            book.title_en = book.title
            book.title_zh = book.title
        if not book.description_en and hasattr(book, 'description'):
            book.description_en = book.description
            book.description_zh = book.description
        book.save()

    # Copy BookChapter data
    for chapter in BookChapter.objects.all():
        if not chapter.title_en and hasattr(chapter, 'title'):
            chapter.title_en = chapter.title
            chapter.title_zh = chapter.title
        if not chapter.description_en and hasattr(chapter, 'description'):
            chapter.description_en = chapter.description
            chapter.description_zh = chapter.description
        if not chapter.grammar_points_en and hasattr(chapter, 'grammar_points'):
            chapter.grammar_points_en = chapter.grammar_points
            chapter.grammar_points_zh = chapter.grammar_points
        if not chapter.cultural_notes_en and hasattr(chapter, 'cultural_notes'):
            chapter.cultural_notes_en = chapter.cultural_notes
            chapter.cultural_notes_zh = chapter.cultural_notes
        chapter.save()

def copy_data_backward(apps, schema_editor):
    # No backward operation needed since old fields are removed
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('mandarin_vocab', '0005_remove_bookchapter_cultural_notes_and_more'),
    ]

    operations = [
        migrations.RunPython(copy_data_forward, copy_data_backward),
    ] 