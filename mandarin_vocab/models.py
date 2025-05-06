from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class VocabularyWord(models.Model):
    HSK_LEVELS = [
        (1, 'HSK1'),
        (2, 'HSK2'),
        (3, 'HSK3'),
        (4, 'HSK4'),
        (5, 'HSK5'),
        (6, 'HSK6'),
    ]

    chinese = models.CharField(max_length=50)
    pinyin = models.CharField(max_length=100)
    english = models.CharField(max_length=200)
    hsk_level = models.IntegerField(choices=HSK_LEVELS, validators=[MinValueValidator(1), MaxValueValidator(6)])
    stroke_order_gif = models.FileField(upload_to='stroke_orders/', null=True, blank=True)
    audio = models.FileField(upload_to='word_audio/', null=True, blank=True)
    example_sentence = models.TextField(blank=True)
    example_pinyin = models.TextField(blank=True)
    example_translation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['hsk_level', 'chinese']
        verbose_name = 'Vocabulary Word'
        verbose_name_plural = 'Vocabulary Words'

    def __str__(self):
        return f"{self.chinese} ({self.pinyin}) - {self.english} [HSK{self.hsk_level}]"

class UserVocabulary(models.Model):
    user = models.ForeignKey('user_auth.CustomUser', on_delete=models.CASCADE)
    word = models.ForeignKey(VocabularyWord, on_delete=models.CASCADE)
    is_learned = models.BooleanField(default=False)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    review_count = models.IntegerField(default=0)
    next_review = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Vocabulary'
        verbose_name_plural = 'User Vocabularies'
        unique_together = ['user', 'word']

    def __str__(self):
        return f"{self.user.username} - {self.word.chinese}"

class HSKBook(models.Model):
    BOOK_TYPES = [
        ('TB', 'Textbook'),
        ('TBA', 'Textbook A'),
        ('TBB', 'Textbook B'),
        ('WB', 'Workbook'),
    ]

    title_en = models.CharField(max_length=200, help_text='English title', null=True, blank=True)
    title_zh = models.CharField(max_length=200, help_text='Chinese title', null=True, blank=True)
    hsk_level = models.IntegerField(choices=VocabularyWord.HSK_LEVELS, validators=[MinValueValidator(1), MaxValueValidator(6)])
    book_type = models.CharField(max_length=3, choices=BOOK_TYPES)
    file = models.FileField(upload_to='books/')
    cover_image = models.ImageField(upload_to='book_covers/', null=True, blank=True)
    description_en = models.TextField(blank=True, help_text='English description', null=True)
    description_zh = models.TextField(blank=True, help_text='Chinese description', null=True)
    page_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['hsk_level', 'book_type']
        verbose_name = 'HSK Book'
        verbose_name_plural = 'HSK Books'
        unique_together = ['hsk_level', 'book_type']

    def __str__(self):
        return f"HSK{self.hsk_level} - {self.get_book_type_display()}"

    @property
    def title(self):
        """Get title based on current language context"""
        from django.utils.translation import get_language
        return self.title_zh if get_language() == 'zh' else self.title_en

    @property
    def description(self):
        """Get description based on current language context"""
        from django.utils.translation import get_language
        return self.description_zh if get_language() == 'zh' else self.description_en

    @property
    def file_url(self):
        return self.file.url if self.file else None

    @property
    def cover_url(self):
        return self.cover_image.url if self.cover_image else None

class BookChapter(models.Model):
    book = models.ForeignKey(HSKBook, on_delete=models.CASCADE, related_name='chapters')
    chapter_number = models.IntegerField()
    title_en = models.CharField(max_length=200, help_text='English title', null=True, blank=True)
    title_zh = models.CharField(max_length=200, help_text='Chinese title', null=True, blank=True)
    description_en = models.TextField(blank=True, help_text='English description', null=True)
    description_zh = models.TextField(blank=True, help_text='Chinese description', null=True)
    start_page = models.IntegerField()
    end_page = models.IntegerField()
    pdf_file = models.FileField(upload_to='book_chapters/', null=True, blank=True)
    vocabulary_list = models.ManyToManyField(VocabularyWord, blank=True, related_name='chapters')
    
    # Text content fields
    chinese_text = models.TextField(blank=True, help_text='Lesson text in Chinese')
    pinyin_text = models.TextField(blank=True, help_text='Pinyin for the lesson text')
    english_text = models.TextField(blank=True, help_text='English translation of the lesson text')
    
    # Grammar points and notes
    grammar_points_en = models.TextField(blank=True, help_text='Key grammar points covered in the lesson (English)', null=True)
    grammar_points_zh = models.TextField(blank=True, help_text='Key grammar points covered in the lesson (Chinese)', null=True)
    cultural_notes_en = models.TextField(blank=True, help_text='Cultural context and notes (English)', null=True)
    cultural_notes_zh = models.TextField(blank=True, help_text='Cultural context and notes (Chinese)', null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['book', 'chapter_number']
        verbose_name = 'Book Chapter'
        verbose_name_plural = 'Book Chapters'
        unique_together = ['book', 'chapter_number']

    def __str__(self):
        return f"{self.book.title} - Chapter {self.chapter_number}: {self.title}"

    @property
    def title(self):
        """Get title based on current language context"""
        from django.utils.translation import get_language
        return self.title_zh if get_language() == 'zh' else self.title_en

    @property
    def description(self):
        """Get description based on current language context"""
        from django.utils.translation import get_language
        return self.description_zh if get_language() == 'zh' else self.description_en

    @property
    def grammar_points(self):
        """Get grammar points based on current language context"""
        from django.utils.translation import get_language
        return self.grammar_points_zh if get_language() == 'zh' else self.grammar_points_en

    @property
    def cultural_notes(self):
        """Get cultural notes based on current language context"""
        from django.utils.translation import get_language
        return self.cultural_notes_zh if get_language() == 'zh' else self.cultural_notes_en

    @property
    def file_url(self):
        return self.pdf_file.url if self.pdf_file else None
