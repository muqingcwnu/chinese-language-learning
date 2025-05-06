from django.core.management.base import BaseCommand
from main_core.models import GrammarLesson
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Load grammar data from text files'

    def determine_category(self, path, title):
        """Determine category based on the path and title."""
        # Check title first for more specific categorization
        title_lower = title.lower()
        if '吗' in title or '呢' in title or '吧' in title or '啊' in title or 'question' in title_lower:
            return 'sentence'
        elif '了' in title or '过' in title or '的' in title or 'particle' in title_lower:
            return 'particles'
        elif 'verb' in title_lower or 'action' in title_lower or '是' in title:
            return 'basic'
        elif 'compare' in title_lower or 'express' in title_lower:
            return 'intermediate'
        elif 'although' in title_lower or 'unless' in title_lower or 'even if' in title_lower:
            return 'advanced'
        
        # If title doesn't give clear category, check path
        path_lower = path.lower()
        if 'basic' in path_lower:
            return 'basic'
        elif 'intermediate' in path_lower:
            return 'intermediate'
        elif 'advanced' in path_lower:
            return 'advanced'
        elif 'particles' in path_lower:
            return 'particles'
        elif 'sentence' in path_lower or 'question' in path_lower:
            return 'sentence'
        
        # Default to basic if no clear category is found
        return 'basic'

    def handle(self, *args, **kwargs):
        try:
            # Path to grammar data files
            grammar_dir = os.path.join(settings.BASE_DIR, 'static', 'data', 'grammar')
            self.stdout.write(f'Looking for grammar files in: {grammar_dir}')
            
            if not os.path.exists(grammar_dir):
                self.stdout.write(self.style.ERROR(f'Directory not found: {grammar_dir}'))
                return
            
            # Clear existing grammar lessons
            GrammarLesson.objects.all().delete()
            self.stdout.write('Cleared existing grammar lessons')
            
            # Process each HSK level file
            for level in range(1, 7):
                filename = f'hsk{level}_grammar_list.txt'
                file_path = os.path.join(grammar_dir, filename)
                
                if not os.path.exists(file_path):
                    self.stdout.write(self.style.WARNING(f'File not found: {filename}'))
                    continue
                
                lessons_count = 0
                category_counts = {
                    'basic': 0,
                    'intermediate': 0,
                    'advanced': 0,
                    'particles': 0,
                    'sentence': 0
                }
                
                self.stdout.write(f'Processing file: {file_path}')
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        for line_num, line in enumerate(file, 1):
                            try:
                                # Split the line by tabs
                                parts = line.strip().split('\t')
                                if len(parts) >= 5:
                                    path = parts[0]
                                    grammar_id = parts[1]
                                    title = parts[2]
                                    pattern = parts[3]
                                    example = parts[4]
                                    
                                    # Determine category based on path and title
                                    category = self.determine_category(path, title)
                                    category_counts[category] += 1
                                    
                                    # Create grammar lesson
                                    GrammarLesson.objects.create(
                                        grammar_id=grammar_id,
                                        title_en=title,
                                        title_zh=title,  # You might want to add Chinese titles later
                                        pattern_en=pattern,
                                        pattern_zh=pattern,  # You might want to add Chinese patterns later
                                        example_en=example,
                                        example_zh=example,  # You might want to add Chinese examples later
                                        hsk_level=level,
                                        category=category
                                    )
                                    lessons_count += 1
                                else:
                                    self.stdout.write(self.style.WARNING(
                                        f'Invalid format in line {line_num} of {filename}'
                                    ))
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(
                                    f'Error processing line {line_num} in HSK{level} file: {str(e)}'
                                ))
                                continue
                                
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully loaded {lessons_count} HSK{level} grammar lessons:'
                    ))
                    for category, count in category_counts.items():
                        if count > 0:
                            self.stdout.write(f'  - {category.title()}: {count} lessons')
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing file {filename}: {str(e)}'))
                    continue
                    
            total_count = GrammarLesson.objects.count()
            self.stdout.write(self.style.SUCCESS(f'Total grammar lessons loaded: {total_count}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}')) 