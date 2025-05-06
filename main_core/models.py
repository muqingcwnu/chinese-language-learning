from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from user_auth.models import CustomUser

# Create your models here.

class GrammarLesson(models.Model):
    CATEGORIES = [
        ('basic', 'Basic Grammar'),
        ('intermediate', 'Intermediate Grammar'),
        ('advanced', 'Advanced Grammar'),
        ('particles', 'Particles'),
        ('sentence', 'Sentence Patterns'),
    ]

    grammar_id = models.CharField(max_length=50, unique=True)
    title_en = models.CharField(max_length=200, help_text='English title', null=True, blank=True)
    title_zh = models.CharField(max_length=200, help_text='Chinese title', null=True, blank=True)
    pattern_en = models.TextField(help_text='Grammar pattern in English', null=True, blank=True)
    pattern_zh = models.TextField(help_text='Grammar pattern in Chinese', null=True, blank=True)
    example_en = models.TextField(help_text='Example in English', null=True, blank=True)
    example_zh = models.TextField(help_text='Example in Chinese', null=True, blank=True)
    hsk_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        default=1
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORIES,
        default='basic'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['hsk_level', 'grammar_id']
        verbose_name = 'Grammar Lesson'
        verbose_name_plural = 'Grammar Lessons'

    def __str__(self):
        return f"HSK{self.hsk_level} - {self.title} ({self.grammar_id})"

    @property
    def title(self):
        """Get title based on current language context"""
        from django.utils.translation import get_language
        return self.title_zh if get_language() == 'zh' else self.title_en

    @property
    def pattern(self):
        """Get pattern based on current language context"""
        from django.utils.translation import get_language
        return self.pattern_zh if get_language() == 'zh' else self.pattern_en

    @property
    def example(self):
        """Get example based on current language context"""
        from django.utils.translation import get_language
        return self.example_zh if get_language() == 'zh' else self.example_en

class UserLesson(models.Model):
    user = models.ForeignKey('user_auth.CustomUser', on_delete=models.CASCADE)
    lesson = models.ForeignKey(GrammarLesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Lesson'
        verbose_name_plural = 'User Lessons'
        unique_together = ['user', 'lesson']
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"

class Quiz(models.Model):
    QUIZ_TYPES = [
        ('vocab', 'Vocabulary'),
        ('grammar', 'Grammar'),
        ('sentence', 'Sentence Rearrange')
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES)
    hsk_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.user.username}'s {self.quiz_type} Quiz - HSK{self.hsk_level}"

    @property
    def duration(self):
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

class QuizQuestion(models.Model):
    QUESTION_TYPES = [
        ('vocab', 'Vocabulary (2 points)'),
        ('grammar', 'Grammar (4 points)'),
        ('sentence', 'Sentence Rearrange (4 points)')
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question_text = models.TextField()
    correct_answer = models.TextField()
    options = models.JSONField(null=True, blank=True)  # For multiple choice questions
    user_answer = models.TextField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    points = models.IntegerField(default=2)  # Default for vocab, will be set to 4 for grammar/sentence
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Question {self.id} for {self.quiz}"

    def save(self, *args, **kwargs):
        # Set points based on question type
        if self.question_type in ['grammar', 'sentence']:
            self.points = 4
        super().save(*args, **kwargs)

class TimelinePost(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('friends', 'Friends Only'),
        ('private', 'Private')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='main_core_posts')
    content = models.TextField()
    image = models.ImageField(upload_to='timeline_images/', null=True, blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mentioned_users = models.ManyToManyField(CustomUser, related_name='main_core_mentions', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s post - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Comment(models.Model):
    post = models.ForeignKey(TimelinePost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='main_core_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    mentioned_users = models.ManyToManyField(CustomUser, related_name='main_core_comment_mentions', blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"

class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('haha', '😄'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😠')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='main_core_reactions')
    post = models.ForeignKey(TimelinePost, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'post']
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}'s {self.reaction_type} on {self.post}"

class UserConnection(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='main_core_connections')
    connected_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='main_core_connected_by')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined')
    ])

    class Meta:
        unique_together = ['user', 'connected_to']

    def __str__(self):
        return f"{self.user.username} -> {self.connected_to.username} ({self.status})"

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('message', 'New Message'),
        ('friend_request', 'Friend Request'),
        ('friend_accept', 'Friend Request Accepted'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.username} from {self.sender.username}"
