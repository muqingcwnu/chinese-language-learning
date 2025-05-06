from django.contrib import admin
from .models import VocabularyWord, UserVocabulary, HSKBook

@admin.register(VocabularyWord)
class VocabularyWordAdmin(admin.ModelAdmin):
    list_display = ('chinese', 'pinyin', 'english', 'hsk_level')
    list_filter = ('hsk_level',)
    search_fields = ('chinese', 'pinyin', 'english')
    ordering = ('hsk_level', 'chinese')

@admin.register(UserVocabulary)
class UserVocabularyAdmin(admin.ModelAdmin):
    list_display = ('user', 'word', 'is_learned', 'last_reviewed', 'review_count')
    list_filter = ('is_learned', 'word__hsk_level')
    search_fields = ('user__username', 'word__chinese')
    ordering = ('-last_reviewed',)

@admin.register(HSKBook)
class HSKBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'hsk_level', 'book_type', 'page_count')
    list_filter = ('hsk_level', 'book_type')
    search_fields = ('title', 'description')
    ordering = ('hsk_level', 'book_type')
