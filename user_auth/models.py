from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUser(AbstractUser):
    PROFICIENCY_LEVELS = [
        ('HSK1', 'HSK Level 1'),
        ('HSK2', 'HSK Level 2'),
        ('HSK3', 'HSK Level 3'),
        ('HSK4', 'HSK Level 4'),
        ('HSK5', 'HSK Level 5'),
        ('HSK6', 'HSK Level 6'),
    ]

    # Personal Information
    full_name = models.CharField(max_length=255, blank=True)
    age = models.IntegerField(validators=[MinValueValidator(5), MaxValueValidator(120)], null=True, blank=True)
    institute = models.CharField(max_length=255, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    
    # Academic Information
    batch = models.CharField(max_length=50, blank=True, help_text='e.g., 2020-2024')
    student_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    university_field = models.CharField(max_length=100, blank=True, help_text='e.g., Computer Science, Business, etc.')
    phone = models.CharField(max_length=20, blank=True)
    
    # Profile and Progress
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    current_hsk_level = models.CharField(max_length=4, choices=PROFICIENCY_LEVELS, default='HSK1')
    learning_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    points = models.IntegerField(default=0)
    completed_lessons = models.IntegerField(default=0)
    
    def __str__(self):
        return self.full_name if self.full_name else self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
