import os
from django.core.management.base import BaseCommand
from main_core.models import GrammarLesson

class Command(BaseCommand):
    help = 'Import grammar lessons from HSK grammar list files'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory containing HSK grammar files')

    def determine_hsk_level(self, filename):
        """Extract HSK level from filename."""
        try:
            return int(filename[3])  # Extract number from 'hskX_grammar_list.txt'
        except (IndexError, ValueError):
            return 1  # Default to HSK1 if can't determine level

    def determine_category(self, title, pattern):
        """Determine the category based on the title and pattern."""
        title_lower = title.lower()
        pattern_lower = pattern.lower()
        
        if any(word in title_lower for word in ['negation', '不', '没']):
            return 'basic'
        elif any(word in pattern_lower for word in ['了', '过', '的']):
            return 'particles'
        elif any(word in title_lower for word in ['sentence', 'order', 'structure']):
            return 'sentence'
        elif any(word in title_lower for word in ['advanced', 'complex']):
            return 'advanced'
        elif any(word in pattern_lower for word in ['吗', '呢', '吧', '啊']):
            return 'particles'
        else:
            return 'intermediate'

    def handle(self, *args, **options):
        directory = options['directory']
        if not os.path.exists(directory):
            self.stdout.write(self.style.ERROR(f'Directory not found: {directory}'))
            return

        # Clear existing grammar lessons if needed
        if GrammarLesson.objects.exists():
            confirm = input('Existing grammar lessons found. Clear them? (y/n): ')
            if confirm.lower() == 'y':
                GrammarLesson.objects.all().delete()
                self.stdout.write('Cleared existing grammar lessons')

        # Process each HSK level file
        for filename in sorted(os.listdir(directory)):
            if not filename.endswith('_grammar_list.txt'):
                continue

            hsk_level = self.determine_hsk_level(filename)
            file_path = os.path.join(directory, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        try:
                            # Split the line by tabs
                            parts = line.strip().split('\t')
                            if len(parts) >= 5:
                                path = parts[0]
                                grammar_id = parts[1]
                                title = parts[2]
                                pattern = parts[3]
                                example = parts[4]

                                # Determine category based on content
                                category = self.determine_category(title, pattern)

                                # Create grammar lesson
                                lesson = GrammarLesson.objects.create(
                                    grammar_id=grammar_id,
                                    title=title,
                                    pattern=pattern,
                                    example=example,
                                    category=category,
                                    hsk_level=hsk_level
                                )

                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'Successfully imported grammar lesson: {lesson}'
                                    )
                                )

                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(
                                    f'Error processing line in {filename}: {str(e)}'
                                )
                            )
                            continue

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error processing file {filename}: {str(e)}'
                    )
                )
                continue

        total_lessons = GrammarLesson.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\nImport completed. Total grammar lessons in database: {total_lessons}'
            )
        ) 