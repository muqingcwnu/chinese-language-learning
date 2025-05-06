import os
from django.core.management.base import BaseCommand
from django.conf import settings
from mandarin_vocab.models import HSKBook, BookChapter

class Command(BaseCommand):
    help = 'Import HSK books from static directory'

    def get_chapter_info(self, hsk_level, chapter_num):
        """Get chapter title and description based on HSK level and chapter number."""
        titles = {
            1: [
                "Greetings and Basic Phrases",
                "Numbers and Counting",
                "Family Members",
                "Time and Date",
                "Food and Drinks",
                "Daily Activities",
                "Places and Directions",
                "Shopping and Money",
                "Weather and Seasons",
                "Basic Conversations"
            ],
            2: [
                "School and Education",
                "Work and Occupations",
                "Hobbies and Interests",
                "Transportation",
                "Health and Body",
                "Clothing and Colors",
                "House and Furniture",
                "Entertainment",
                "Travel and Tourism",
                "Making Plans"
            ],
            3: [
                "Social Relationships",
                "Business and Economy",
                "Technology and Internet",
                "Environment and Nature",
                "Culture and Traditions",
                "Sports and Exercise",
                "News and Media",
                "Art and Literature",
                "Emotions and Feelings",
                "Personal Development"
            ],
            4: [
                "Academic Studies",
                "Career Development",
                "Science and Research",
                "Society and Politics",
                "Law and Justice",
                "Medicine and Healthcare",
                "International Relations",
                "Philosophy and Religion",
                "History and Civilization",
                "Modern Life Challenges"
            ],
            5: [
                "Advanced Communication",
                "Economic Development",
                "Cultural Exchange",
                "Scientific Innovation",
                "Global Challenges",
                "Social Philosophy",
                "Literary Analysis",
                "Political Systems",
                "Historical Perspectives",
                "Contemporary Issues"
            ],
            6: [
                "Academic Writing",
                "Professional Communication",
                "Research Methodology",
                "Critical Analysis",
                "Cultural Studies",
                "Advanced Literature",
                "International Affairs",
                "Theoretical Frameworks",
                "Comparative Studies",
                "Modern China"
            ]
        }

        descriptions = {
            1: "Basic vocabulary and simple conversations for everyday situations.",
            2: "Elementary grammar and practical communication skills.",
            3: "Intermediate language skills for broader social interaction.",
            4: "Upper-intermediate content for professional and academic contexts.",
            5: "Advanced language mastery for complex topics.",
            6: "Superior language proficiency for academic and professional excellence."
        }

        if 0 < chapter_num <= len(titles[hsk_level]):
            return {
                'title': titles[hsk_level][chapter_num - 1],
                'description': f"HSK{hsk_level} Chapter {chapter_num}: {titles[hsk_level][chapter_num - 1]}. {descriptions[hsk_level]}"
            }
        return None

    def handle(self, *args, **options):
        books_dir = os.path.join(settings.BASE_DIR, 'static', 'data', 'books')
        
        for level in range(1, 7):
            hsk_dir = os.path.join(books_dir, f'hsk{level}')
            if not os.path.exists(hsk_dir):
                self.stdout.write(self.style.WARNING(f'Directory not found for HSK{level}'))
                continue

            # Create or update the book
            book, created = HSKBook.objects.get_or_create(
                hsk_level=level,
                book_type='TB',
                defaults={
                    'title': f'HSK{level} Standard Course Textbook',
                    'description': f'Official HSK{level} textbook for standard course curriculum.',
                    'page_count': 200  # Default page count
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created book for HSK{level}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated book for HSK{level}'))

            # Create chapters for the book
            for chapter_num in range(1, 11):  # 10 chapters per book
                chapter_info = self.get_chapter_info(level, chapter_num)
                if chapter_info:
                    chapter, created = BookChapter.objects.get_or_create(
                        book=book,
                        chapter_number=chapter_num,
                        defaults={
                            'title': chapter_info['title'],
                            'description': chapter_info['description'],
                            'start_page': (chapter_num - 1) * 20 + 1,  # Estimate 20 pages per chapter
                            'end_page': chapter_num * 20
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created chapter {chapter_num} for HSK{level}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated chapter {chapter_num} for HSK{level}')) 