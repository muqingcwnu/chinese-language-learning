from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.utils import timezone
from .models import VocabularyWord, UserVocabulary, HSKBook

def vocab_home(request):
    hsk_stats = []
    for level in range(1, 7):
        word_count = VocabularyWord.objects.filter(hsk_level=level).count()
        if request.user.is_authenticated:
            learned_count = UserVocabulary.objects.filter(
                user=request.user,
                word__hsk_level=level,
                is_learned=True
            ).count()
        else:
            learned_count = 0
        
        hsk_stats.append({
            'level': level,
            'total_words': word_count,
            'learned_words': learned_count,
            'progress': (learned_count / word_count * 100) if word_count > 0 else 0
        })
    
    return render(request, 'mandarin_vocab/home.html', {
        'hsk_stats': hsk_stats
    })

def hsk_level(request, level):
    words = VocabularyWord.objects.filter(hsk_level=level)
    if request.user.is_authenticated:
        learned_words = UserVocabulary.objects.filter(
            user=request.user,
            word__in=words,
            is_learned=True
        ).values_list('word_id', flat=True)
    else:
        learned_words = []
    
    return render(request, 'mandarin_vocab/hsk_level.html', {
        'level': level,
        'words': words,
        'learned_words': learned_words
    })

def word_detail(request, word_id):
    word = get_object_or_404(VocabularyWord, id=word_id)
    if request.user.is_authenticated:
        user_vocab, created = UserVocabulary.objects.get_or_create(
            user=request.user,
            word=word
        )
    else:
        user_vocab = None
    
    return render(request, 'mandarin_vocab/word_detail.html', {
        'word': word,
        'user_vocab': user_vocab
    })

@login_required
def my_vocabulary(request):
    user_vocab = UserVocabulary.objects.filter(
        user=request.user,
        is_learned=True
    ).select_related('word').order_by('word__hsk_level', 'word__chinese')
    
    return render(request, 'mandarin_vocab/my_vocabulary.html', {
        'user_vocab': user_vocab
    })

@login_required
def toggle_learned(request, word_id):
    word = get_object_or_404(VocabularyWord, id=word_id)
    user_vocab, created = UserVocabulary.objects.get_or_create(
        user=request.user,
        word=word
    )
    
    user_vocab.is_learned = not user_vocab.is_learned
    if user_vocab.is_learned:
        user_vocab.last_reviewed = timezone.now()
        user_vocab.review_count += 1
    user_vocab.save()
    
    return JsonResponse({
        'status': 'success',
        'is_learned': user_vocab.is_learned
    })

def get_audio(request, word_id):
    word = get_object_or_404(VocabularyWord, id=word_id)
    if word.audio:
        return FileResponse(word.audio)
    return JsonResponse({'error': 'No audio file available'}, status=404)

def books(request):
    books = HSKBook.objects.all().order_by('hsk_level', 'book_type')
    return render(request, 'mandarin_vocab/books.html', {
        'books': books
    })
