import csv
import os
from django.core.management.base import BaseCommand
from mandarin_vocab.models import VocabularyWord

class Command(BaseCommand):
    help = 'Import vocabulary from tab-separated CSV files'

    def handle(self, *args, **options):
        base_dir = os.path.join('static', 'data', 'vocab')
        
        # Create directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)
        
        # Clear existing vocabulary
        VocabularyWord.objects.all().delete()
        self.stdout.write('Cleared existing vocabulary')

        # Process each HSK level
        for level in range(1, 7):
            file_path = os.path.join(base_dir, f'hsk{level}_vocab.csv')
            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(f'File not found: {file_path}'))
                continue

            words_created = 0
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Use tab as delimiter
                    reader = csv.reader(file, delimiter='\t')
                    for row_num, row in enumerate(reader, 1):
                        self.stdout.write(f'Processing row {row_num} in HSK{level}: {row}')
                        if len(row) >= 3:  # Ensure we have chinese, pinyin, and english
                            try:
                                VocabularyWord.objects.create(
                                    chinese=row[0].strip(),
                                    pinyin=row[1].strip(),
                                    english=row[2].strip(),
                                    hsk_level=level
                                )
                                words_created += 1
                            except Exception as e:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'Error importing word {row[0]} at row {row_num}: {str(e)}'
                                    )
                                )
                                continue

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully imported {words_created} words for HSK{level}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing file for HSK{level}: {str(e)}'
                    )
                )
                continue

        total_words = VocabularyWord.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Import completed. Total words in database: {total_words}'
            )
        ) 