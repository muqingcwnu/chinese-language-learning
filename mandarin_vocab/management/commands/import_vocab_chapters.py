import os
import csv
from django.core.management.base import BaseCommand
from mandarin_vocab.models import VocabularyWord, HSKBook, BookChapter
from django.conf import settings

class Command(BaseCommand):
    help = 'Import vocabulary words and associate them with book chapters'

    def handle(self, *args, **options):
        vocab_dir = os.path.join(settings.BASE_DIR, 'static', 'data', 'vocab')
        
        for level in range(1, 7):
            vocab_file = os.path.join(vocab_dir, f'hsk{level}_vocab.csv')
            if not os.path.exists(vocab_file):
                self.stdout.write(self.style.WARNING(f'Vocabulary file not found for HSK{level}'))
                continue

            # Get the book for this HSK level
            try:
                book = HSKBook.objects.get(hsk_level=level, book_type='TB')
            except HSKBook.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Book not found for HSK{level}'))
                continue

            # Get all chapters for this book
            chapters = list(book.chapters.all().order_by('chapter_number'))
            if not chapters:
                self.stdout.write(self.style.WARNING(f'No chapters found for HSK{level} book'))
                continue

            # Read vocabulary words
            with open(vocab_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter='\t')
                words = list(reader)

            # Calculate words per chapter (distribute evenly)
            words_per_chapter = len(words) // len(chapters)
            extra_words = len(words) % len(chapters)

            # Process each chapter
            word_index = 0
            for chapter in chapters:
                # Calculate how many words for this chapter
                chapter_word_count = words_per_chapter + (1 if extra_words > 0 else 0)
                extra_words -= 1

                # Get words for this chapter
                chapter_words = words[word_index:word_index + chapter_word_count]
                word_index += chapter_word_count

                # Process each word
                for word_data in chapter_words:
                    if len(word_data) >= 3:  # Make sure we have chinese, pinyin, and english
                        # Try to find existing word
                        existing_words = VocabularyWord.objects.filter(
                            chinese=word_data[0],
                            pinyin=word_data[1],
                            english=word_data[2]
                        )
                        
                        if existing_words.exists():
                            word = existing_words.first()
                        else:
                            word = VocabularyWord.objects.create(
                                chinese=word_data[0],
                                pinyin=word_data[1],
                                english=word_data[2],
                                hsk_level=level
                            )
                        
                        # Add word to chapter if not already present
                        if word not in chapter.vocabulary_list.all():
                            chapter.vocabulary_list.add(word)

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Added {len(chapter_words)} words to HSK{level} Chapter {chapter.chapter_number}: {chapter.title}'
                    )
                )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully processed vocabulary for HSK{level}')
            ) 