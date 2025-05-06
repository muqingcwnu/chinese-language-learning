import csv
import os
from django.core.management.base import BaseCommand
from mandarin_vocab.models import VocabularyWord

class Command(BaseCommand):
    help = 'Import HSK1 vocabulary from tab-separated CSV file'

    def handle(self, *args, **options):
        # Clear existing HSK1 vocabulary
        VocabularyWord.objects.filter(hsk_level=1).delete()
        self.stdout.write('Cleared existing HSK1 vocabulary')

        file_path = os.path.join('static', 'data', 'vocab', 'hsk1_vocab.csv')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        words_created = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter='\t')
                for row in reader:
                    if len(row) >= 3:  # Ensure we have chinese, pinyin, and english
                        VocabularyWord.objects.create(
                            chinese=row[0].strip(),
                            pinyin=row[1].strip(),
                            english=row[2].strip(),
                            hsk_level=1
                        )
                        words_created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {words_created} HSK1 words'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error processing HSK1 file: {str(e)}'
                )
            ) 