from django.core.management.base import BaseCommand
from mandarin_vocab.models import HSKBook, BookChapter

class Command(BaseCommand):
    help = 'Create HSK books and their chapters'

    def handle(self, *args, **options):
        # Create HSK1 Book
        hsk1_book, created = HSKBook.objects.get_or_create(
            hsk_level=1,
            book_type='TB',
            defaults={
                'title': 'HSK1 Standard Course Textbook',
                'description': 'Official HSK1 textbook for standard course curriculum.',
                'page_count': 200
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created HSK1 book: {hsk1_book.title}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'HSK1 book already exists: {hsk1_book.title}'))

        # Create chapters for HSK1
        chapters = [
            {"title": "Greetings and Basic Phrases", "description": "Learn basic greetings and everyday phrases."},
            {"title": "Numbers and Counting", "description": "Master numbers and basic counting in Mandarin."},
            {"title": "Family Members", "description": "Learn vocabulary for family relationships."},
            {"title": "Time and Date", "description": "Express time and dates in Mandarin."},
            {"title": "Food and Drinks", "description": "Basic vocabulary for food and beverages."},
            {"title": "Daily Activities", "description": "Common verbs and daily routine expressions."},
            {"title": "Places and Directions", "description": "Navigate and describe locations."},
            {"title": "Shopping and Money", "description": "Basic shopping and transaction vocabulary."},
            {"title": "Weather and Seasons", "description": "Describe weather and seasonal changes."},
            {"title": "Basic Conversations", "description": "Put it all together in simple dialogues."}
        ]

        for index, chapter_data in enumerate(chapters, 1):
            chapter, created = BookChapter.objects.get_or_create(
                book=hsk1_book,
                chapter_number=index,
                defaults={
                    'title': chapter_data['title'],
                    'description': chapter_data['description'],
                    'start_page': (index - 1) * 20 + 1,
                    'end_page': index * 20
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created chapter {index}: {chapter.title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Chapter {index} already exists: {chapter.title}')) 