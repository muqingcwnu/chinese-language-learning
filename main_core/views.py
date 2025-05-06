from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, FileResponse, HttpResponse, Http404
from django.contrib.auth import login, logout, authenticate
from utils.deepseek_api import deepseek_api, DeepSeekAPI
from .models import GrammarLesson, Quiz, QuizQuestion, UserLesson
from django.db.models import Count
from mandarin_vocab.models import HSKBook, BookChapter, VocabularyWord, UserVocabulary
from itertools import groupby
from django.db.models import Prefetch
from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import static
from django.utils import timezone
import json
import random
from datetime import datetime
from django.db import models
from .models import TimelinePost, Comment, Reaction, UserConnection, CustomUser, Message, Notification
import os
from django.conf import settings as django_settings
from .utils import get_grammar_explanation
from decouple import config
import logging
from django.core.files.storage import default_storage
from user_auth.forms import CustomUserCreationForm, UserSettingsForm
import csv
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)

def change_language(request):
    """
    Change the language setting for the current session.
    Supports 'en' (English) and 'zh' (Chinese).
    """
    lang = request.GET.get('lang', 'en')
    if lang not in ['en', 'zh']:
        lang = 'en'
    
    # Set the language in session
    request.session['language'] = lang
    request.session.modified = True
    
    # Log the language change
    logger.info(f"Language changed to {lang} for user {request.user if request.user.is_authenticated else 'anonymous'}")
    
    # Get the previous page from the referer header or default to home
    next_page = request.META.get('HTTP_REFERER')
    if not next_page or '/admin/' in next_page:  # Don't redirect back to admin
        next_page = '/'
        
    return redirect(next_page)

def home(request):
    """Home page view."""
    return render(request, 'main_core/home.html')

def about(request):
    return render(request, 'about.html')

def privacy(request):
    return render(request, 'privacy.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Send email
        try:
            send_mail(
                f'Contact Form Message from {name}',
                f'From: {name}\nEmail: {email}\n\nMessage:\n{message}',
                email,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            messages.error(request, 'There was an error sending your message. Please try again later.')
        
    return render(request, 'contact.html')

@login_required
def ai_assistant(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            try:
                response = deepseek_api.generate_response(user_message)
                # Since generate_response now always returns a string (either response or error message)
                return JsonResponse({'response': response})
            except Exception as e:
                return JsonResponse({'error': 'An unexpected error occurred. Please try again.'}, status=500)
    return render(request, 'main_core/ai_assistant.html')

@login_required
def grammar_home(request):
    # Get statistics for each HSK level
    hsk_levels = []
    for level in range(1, 7):
        level_count = GrammarLesson.objects.filter(hsk_level=level).count()
        if request.user.is_authenticated:
            completed_count = 0  # TODO: Implement progress tracking
            progress = (completed_count / level_count * 100) if level_count > 0 else 0
        else:
            completed_count = 0
            progress = 0
            
        hsk_levels.append({
            'number': level,
            'grammar_count': level_count,
            'completed_count': completed_count,
            'progress': progress
        })

    # Get category statistics
    categories = []
    for code, name in GrammarLesson.CATEGORIES:
        count = GrammarLesson.objects.filter(category=code).count()
        description = get_category_description(code)
        categories.append({
            'code': code,
            'name': name,
            'count': count,
            'description': description
        })

    context = {
        'hsk_levels': hsk_levels,
        'categories': categories,
    }
    return render(request, 'main_core/grammar_home.html', context)

def grammar_level(request, level):
    if not 1 <= level <= 6:
        return redirect('main_core:grammar_home')

    category = request.GET.get('category')
    lessons = GrammarLesson.objects.filter(hsk_level=level)
    
    if category and category != 'all':
        lessons = lessons.filter(category=category)

    categories = [
        {'code': code, 'name': name}
        for code, name in GrammarLesson.CATEGORIES
    ]

    context = {
        'level': level,
        'lessons': lessons,
        'categories': categories,
        'category': category,
    }
    return render(request, 'main_core/grammar_level.html', context)

@login_required
def grammar_category(request, category):
    # Get HSK level filter from query parameters
    hsk_level = request.GET.get('hsk_level')
    
    # Filter lessons by category
    lessons = GrammarLesson.objects.filter(category=category)
    
    # Apply HSK level filter if provided
    if hsk_level and hsk_level.isdigit() and 1 <= int(hsk_level) <= 6:
        lessons = lessons.filter(hsk_level=int(hsk_level))
    
    # Get category name from choices
    category_name = dict(GrammarLesson.CATEGORIES)[category]
    
    return render(request, 'main_core/grammar_category.html', {
        'category': category,
        'category_name': category_name,
        'lessons': lessons,
        'current_hsk_level': hsk_level
    })

@login_required
def grammar_lesson(request, lesson_id):
    """Display a grammar lesson with AI-generated explanations."""
    lesson = get_object_or_404(GrammarLesson, id=lesson_id)
    user_lesson, created = UserLesson.objects.get_or_create(user=request.user, lesson=lesson)
    
    # Get the user's language preference
    language = getattr(request, 'LANGUAGE_CODE', 'en')
    
    try:
        # Initialize DeepSeek API
        deepseek_api = DeepSeekAPI()
        
        # Get detailed explanation from DeepSeek
        explanation = deepseek_api.get_grammar_explanation(
            title=lesson.title,
            pattern=lesson.pattern,
            example=lesson.example,
            language=language
        )
        
        # Log successful response
        logger.info(f"Successfully generated explanation for lesson {lesson_id}")
        
    except ValueError as e:
        logger.error(f"API error for lesson {lesson_id}: {str(e)}")
        messages.error(request, str(e))
        explanation = None
    except Exception as e:
        logger.error(f"Unexpected error for lesson {lesson_id}: {str(e)}", exc_info=True)
        messages.error(request, _("explanation_error_message"))
        explanation = None
    
    context = {
        'lesson': lesson,
        'user_lesson': user_lesson,
        'explanation': explanation,
        'is_completed': user_lesson.is_completed,
        'completed_at': user_lesson.completed_at,
    }
    
    return render(request, 'main_core/grammar_lesson.html', context)

@login_required
def toggle_lesson_completed(request, lesson_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    lesson = get_object_or_404(GrammarLesson, id=lesson_id)
    user_lesson, created = UserLesson.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )
    
    user_lesson.is_completed = not user_lesson.is_completed
    if user_lesson.is_completed:
        user_lesson.completed_at = timezone.now()
    user_lesson.save()
    
    return JsonResponse({
        'status': 'success',
        'is_completed': user_lesson.is_completed,
        'completed_at': user_lesson.completed_at.isoformat() if user_lesson.completed_at else None
    })

def get_category_description(category_code):
    descriptions = {
        'basic': 'Fundamental grammar patterns essential for daily communication.',
        'intermediate': 'More complex patterns for expressing detailed thoughts.',
        'advanced': 'Sophisticated grammar structures for formal and academic contexts.',
        'particles': 'Essential particles that modify meaning and tone.',
        'sentence': 'Common sentence patterns and structures.',
    }
    return descriptions.get(category_code, '')

def lessons_home(request):
    print("\n=== Debug: lessons_home view ===")
    # Get all books ordered by HSK level
    books = HSKBook.objects.all().order_by('hsk_level').prefetch_related(
        Prefetch('chapters', queryset=BookChapter.objects.order_by('chapter_number'))
    )
    print(f"Total books found: {books.count()}")
    
    # Create a dictionary to store books by level
    books_by_level = {}
    hsk_levels = range(1, 7)  # HSK levels 1-6
    
    # Group books by HSK level
    for book in books:
        print(f"Processing book: {book.title} (HSK{book.hsk_level})")
        level = book.hsk_level
        if level not in books_by_level:
            books_by_level[level] = []
        books_by_level[level].append({
            'book': book,
            'chapters': book.chapters.all()
        })
    
    print("Books grouped by level:", {k: len(v) for k, v in books_by_level.items()})
    print("=== End Debug ===\n")
    
    context = {
        'books_by_level': books_by_level,
        'hsk_levels': hsk_levels,
    }
    
    return render(request, 'main_core/lessons_home.html', context)

@login_required
def lesson_detail(request, book_id, chapter_number):
    book = get_object_or_404(HSKBook, id=book_id)
    chapter = get_object_or_404(BookChapter, book=book, chapter_number=chapter_number)
    
    # Get next and previous chapters
    next_chapter = BookChapter.objects.filter(
        book=book, 
        chapter_number__gt=chapter_number
    ).order_by('chapter_number').first()
    
    prev_chapter = BookChapter.objects.filter(
        book=book, 
        chapter_number__lt=chapter_number
    ).order_by('-chapter_number').first()
    
    context = {
        'book': book,
        'chapter': chapter,
        'next_chapter': next_chapter,
        'prev_chapter': prev_chapter,
    }
    
    return render(request, 'main_core/lesson_detail.html', context)

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(HSKBook, id=book_id)
    chapters = book.chapters.all().order_by('chapter_number')
    
    context = {
        'book': book,
        'chapters': chapters,
    }
    
    return render(request, 'main_core/book_detail.html', context)

@login_required
def tasks_home(request):
    return render(request, 'main_core/tasks_home.html')

@login_required
def quiz_home(request):
    """Quiz home page view."""
    try:
        # Initialize DeepSeek API and test connection
        api = DeepSeekAPI()
        connection_status, message = api.test_connection()
        
        if not connection_status:
            messages.warning(request, f"AI service temporarily unavailable: {message}")
        
        # Get quiz statistics
        quiz_stats = Quiz.objects.filter(user=request.user).aggregate(
            total_quizzes=Count('id'),
            completed_quizzes=Count('id', filter=models.Q(completed=True)),
            total_score=models.Sum('score', filter=models.Q(completed=True)) or 0
        )
        
        # Get recent quizzes
        recent_quizzes = Quiz.objects.filter(
            user=request.user,
            completed=True
        ).order_by('-end_time')[:5]
        
        context = {
            'quiz_stats': quiz_stats,
            'recent_quizzes': recent_quizzes,
            'ai_available': connection_status,
            'hsk_levels': range(1, 7)  # Add HSK levels 1-6
        }
        
        return render(request, 'main_core/quiz_home.html', context)
        
    except Exception as e:
        logger.error(f"Error in quiz home: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while loading the quiz page. Please try again later.")
        return render(request, 'main_core/quiz_home.html', {'ai_available': False, 'hsk_levels': range(1, 7)})

@login_required
def timeline_home(request):
    # Get user connections
    user_connections = CustomUser.objects.filter(
        models.Q(main_core_connected_by__user=request.user, main_core_connected_by__status='accepted') |
        models.Q(main_core_connections__connected_to=request.user, main_core_connections__status='accepted')
    ).distinct()

    # Get posts based on visibility
    posts = TimelinePost.objects.filter(
        models.Q(visibility='public') |  # All public posts
        models.Q(user=request.user) |    # All posts by current user
        models.Q(user__in=user_connections, visibility='friends')  # Friends-only posts from connections
    ).order_by('-created_at')

    if request.method == 'POST':
        content = request.POST.get('content')
        visibility = request.POST.get('visibility', 'public')
        
        if content:
            post = TimelinePost.objects.create(
                user=request.user,
                content=content,
                visibility=visibility
            )
            messages.success(request, 'Post created successfully!')
        else:
            messages.error(request, 'Post content cannot be empty.')
        
        return redirect('main_core:timeline_home')

    context = {
        'posts': posts,
        'user_connections': user_connections,
    }
    return render(request, 'main_core/timeline_home.html', context)

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(TimelinePost, id=post_id)
        content = request.POST.get('content')
        
        if content:
            # Extract mentions from content
            mentioned_usernames = [word[1:] for word in content.split() if word.startswith('@')]
            mentioned_users = CustomUser.objects.filter(username__in=mentioned_usernames)
            
            # Create comment
            comment = Comment.objects.create(
                post=post,
                user=request.user,
                content=content
            )
            
            # Add mentions
            comment.mentioned_users.set(mentioned_users)
            
            messages.success(request, 'Comment added successfully!')
    
    return redirect('main_core:timeline_home')

@login_required
def add_reaction(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(TimelinePost, id=post_id)
        reaction_type = request.POST.get('reaction_type')
        
        if reaction_type:
            # Remove existing reaction if any
            Reaction.objects.filter(user=request.user, post=post).delete()
            
            # Add new reaction
            Reaction.objects.create(
                user=request.user,
                post=post,
                reaction_type=reaction_type
            )
            
            messages.success(request, 'Reaction added!')
    
    return redirect('main_core:timeline_home')

@login_required
def user_connections(request):
    # Get user's accepted connections
    connections = CustomUser.objects.filter(
        models.Q(main_core_connected_by__user=request.user, main_core_connected_by__status='accepted') |
        models.Q(main_core_connections__connected_to=request.user, main_core_connections__status='accepted')
    ).distinct().annotate(
        connected_at=models.Min(
            models.Case(
                models.When(main_core_connected_by__user=request.user, then='main_core_connected_by__created_at'),
                models.When(main_core_connections__connected_to=request.user, then='main_core_connections__created_at'),
                default=None
            )
        )
    )
    
    # Get pending friend requests
    pending_requests = UserConnection.objects.filter(
        connected_to=request.user,
        status='pending'
    ).select_related('user')
    
    # Handle search functionality
    search_query = request.GET.get('search', '')
    search_results = None
    if search_query:
        search_results = CustomUser.objects.filter(
            username__icontains=search_query
        ).exclude(
            id=request.user.id
        ).exclude(
            id__in=connections.values_list('id', flat=True)
        )[:10]  # Limit to 10 results
    
    # Get IDs of users to whom we've sent pending requests
    pending_sent_requests = UserConnection.objects.filter(
        user=request.user,
        status='pending'
    ).values_list('connected_to_id', flat=True)
    
    context = {
        'connections': connections,
        'pending_requests': pending_requests,
        'search_query': search_query,
        'search_results': search_results,
        'pending_sent_requests': pending_sent_requests,
    }
    return render(request, 'main_core/user_connections.html', context)

@login_required
def connect_user(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, id=user_id)
        
        # Check if connection already exists
        existing_connection = UserConnection.objects.filter(
            models.Q(user=request.user, connected_to=target_user) |
            models.Q(user=target_user, connected_to=request.user)
        ).first()
        
        if not existing_connection:
            UserConnection.objects.create(
                user=request.user,
                connected_to=target_user,
                status='pending'
            )
            messages.success(request, f'Connection request sent to {target_user.username}!')
        else:
            messages.warning(request, 'Connection already exists or is pending.')
    
    return redirect('main_core:user_connections')

@login_required
def handle_connection_request(request, connection_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action not in ['accept', 'decline']:
                return JsonResponse({'status': 'error', 'message': 'Invalid action'})
            
            connection = get_object_or_404(UserConnection, id=connection_id, connected_to=request.user)
            
            if action == 'accept':
                connection.status = 'accepted'
                connection.save()
                messages.success(request, f'You are now connected with {connection.user.username}!')
            else:
                connection.status = 'declined'
                connection.save()
                messages.success(request, 'Connection request declined.')
            
            return JsonResponse({'status': 'success'})
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def remove_connection(request, connection_id):
    if request.method == 'POST':
        # Get the target user
        target_user = get_object_or_404(CustomUser, id=connection_id)
        
        # Find and delete both directions of the connection
        UserConnection.objects.filter(
            (models.Q(user=request.user, connected_to=target_user) |
             models.Q(user=target_user, connected_to=request.user)) &
            models.Q(status='accepted')
        ).delete()
        
        messages.success(request, 'Connection removed successfully.')
    
    return redirect('main_core:user_connections')

@login_required
def start_quiz(request):
    if request.method == 'POST':
        try:
            quiz_type = request.POST.get('quiz_type')
            hsk_level = int(request.POST.get('hsk_level'))
            
            # Validate input parameters
            if not quiz_type or not hsk_level:
                messages.error(request, "Please select both quiz type and HSK level")
                return redirect('main_core:quiz_home')
            
            # Create new quiz
            quiz = Quiz.objects.create(
                user=request.user,
                quiz_type=quiz_type,
                hsk_level=hsk_level
            )
            
            # Initialize DeepSeek API
            try:
                deepseek = DeepSeekAPI()
                # Test API connection
                connection_success, message = deepseek.test_connection()
                if not connection_success:
                    raise Exception(f"DeepSeek API connection failed: {message}")
            except Exception as e:
                messages.error(request, f"Failed to connect to AI service: {str(e)}")
                quiz.delete()  # Clean up the created quiz
                return redirect('main_core:quiz_home')
            
            if quiz_type == 'vocab':
                # Get user's vocabulary progress
                learned_words = UserVocabulary.objects.filter(
                    user=request.user,
                    word__hsk_level=hsk_level,
                    is_learned=True
                ).values_list('word_id', flat=True)
                
                if not learned_words:
                    messages.warning(request, f"You haven't learned any HSK {hsk_level} vocabulary words yet. Please learn some words first.")
                    quiz.delete()
                    return redirect('main_core:quiz_home')
                
                # Get 5 random words from learned vocabulary
                available_words = VocabularyWord.objects.filter(id__in=learned_words)
                if available_words.count() < 5:
                    messages.warning(request, f"You need at least 5 learned words to take a vocabulary quiz. You currently have {available_words.count()}.")
                    quiz.delete()
                    return redirect('main_core:quiz_home')
                
                selected_words = random.sample(list(available_words), 5)
                
                for word in selected_words:
                    try:
                        # Generate multiple choice options using DeepSeek
                        options = deepseek.generate_vocab_options(word.chinese, word.pinyin, word.english)
                        if not options or len(options) < 3:
                            raise Exception("Failed to generate enough options")
                        
                        all_options = [word.english] + options[:3]
                        random.shuffle(all_options)
                        
                        QuizQuestion.objects.create(
                            quiz=quiz,
                            question_type='vocab',
                            question_text=f"{word.chinese} ({word.pinyin})",
                            correct_answer=word.english,
                            options=all_options
                        )
                    except Exception as e:
                        messages.error(request, f"Error generating vocabulary question: {str(e)}")
                        quiz.delete()
                        return redirect('main_core:quiz_home')
            
            elif quiz_type == 'grammar':
                try:
                    # Generate grammar questions
                    questions = deepseek.generate_grammar_questions(hsk_level, 5)
                    if not questions or len(questions) < 5:
                        raise Exception("Failed to generate enough grammar questions")
                    
                    for q in questions:
                        options = [q['correct_answer']] + q['incorrect_options']
                        random.shuffle(options)
                        
                        QuizQuestion.objects.create(
                            quiz=quiz,
                            question_type='grammar',
                            question_text=q['question_text'],
                            correct_answer=q['correct_answer'],
                            options=options
                        )
                except Exception as e:
                    messages.error(request, f"Error generating grammar questions: {str(e)}")
                    quiz.delete()
                    return redirect('main_core:quiz_home')
            
            else:  # sentence rearrange
                try:
                    # Generate sentence questions
                    sentences = deepseek.generate_sentence_questions(hsk_level, 5)
                    if not sentences or len(sentences) < 5:
                        raise Exception("Failed to generate enough sentence questions")
                    
                    for s in sentences:
                        QuizQuestion.objects.create(
                            quiz=quiz,
                            question_type='sentence',
                            question_text=json.dumps({
                                'scrambled': s['scrambled_words'],
                                'pinyin': s['pinyin'],
                                'english': s['english_translation']
                            }),
                            correct_answer=s['original_sentence']
                        )
                except Exception as e:
                    messages.error(request, f"Error generating sentence questions: {str(e)}")
                    quiz.delete()
                    return redirect('main_core:quiz_home')
            
            # Check if questions were created successfully
            if quiz.questions.count() == 0:
                messages.error(request, "Failed to create quiz questions")
                quiz.delete()
                return redirect('main_core:quiz_home')
            
            return redirect('main_core:take_quiz', quiz_id=quiz.id)
            
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            return redirect('main_core:quiz_home')
    
    return redirect('main_core:quiz_home')

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    
    if quiz.completed:
        return redirect('main_core:quiz_results', quiz_id=quiz.id)
    
    questions = quiz.questions.all()
    
    if request.method == 'POST':
        # Process answers
        for question in questions:
            answer = request.POST.get(f'answer_{question.id}')
            question.user_answer = answer
            question.is_correct = (answer == question.correct_answer)
            question.save()
            
            if question.is_correct:
                quiz.score += question.points
        
        quiz.completed = True
        quiz.end_time = timezone.now()
        quiz.total_questions = questions.count()
        quiz.save()
        
        return redirect('main_core:quiz_results', quiz_id=quiz.id)
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'time_limit': 120,  # 2 minutes in seconds
    }
    return render(request, 'main_core/take_quiz.html', context)

@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, user=request.user)
    questions = quiz.questions.all()
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'total_points': sum(q.points for q in questions),
        'correct_answers': questions.filter(is_correct=True).count(),
    }
    return render(request, 'main_core/quiz_results.html', context)

@login_required
def quiz_history(request):
    # Get all completed quizzes for the user
    quizzes = Quiz.objects.filter(
        user=request.user,
        completed=True
    ).order_by('-start_time')
    
    # Prepare data for the chart
    dates = [quiz.start_time.strftime('%Y-%m-%d %H:%M') for quiz in quizzes]
    scores = [round((quiz.score / sum(q.points for q in quiz.questions.all()) * 100), 1) for quiz in quizzes]
    
    context = {
        'quizzes': quizzes,
        'dates': json.dumps(dates),
        'scores': json.dumps(scores)
    }
    return render(request, 'main_core/quiz_history.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('main_core:home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'main_core/login.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                profile_pic = request.FILES['profile_picture']
                file_path = default_storage.save(f'profile_pictures/{user.username}_{profile_pic.name}', profile_pic)
                user.profile_picture = file_path
                user.save()
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Registration successful!')
            return redirect('main_core:home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('main_core:home')

@login_required
def profile(request):
    # Get user's posts
    user_posts = TimelinePost.objects.filter(user=request.user).order_by('-created_at')
    
    # Get user's connections
    user_connections = UserConnection.objects.filter(
        models.Q(user=request.user) | models.Q(connected_to=request.user),
        status='accepted'
    )
    
    # Get user's learning progress
    completed_quizzes = Quiz.objects.filter(user=request.user, completed=True)
    vocabulary_words = UserVocabulary.objects.filter(user=request.user, is_learned=True)
    completed_lessons = UserLesson.objects.filter(user=request.user, is_completed=True)
    
    # Aggregate daily progress data for the last 30 days
    today = timezone.now().date()
    thirty_days_ago = today - timezone.timedelta(days=30)
    
    daily_progress = []
    for i in range(30):
        date = today - timezone.timedelta(days=i)
        
        # Get metrics for this day
        day_quizzes = completed_quizzes.filter(
            end_time__date=date
        )
        day_vocab = vocabulary_words.filter(
            created_at__date=date
        )
        day_lessons = completed_lessons.filter(
            completed_at__date=date
        )
        
        # Calculate average quiz score for the day
        if day_quizzes.exists():
            day_scores = []
            for quiz in day_quizzes:
                score_percentage = (quiz.score / quiz.total_questions) * 100 if quiz.total_questions > 0 else 0
                day_scores.append(score_percentage)
            avg_score = sum(day_scores) / len(day_scores)
        else:
            avg_score = 0
            
        daily_progress.append({
            'date': date.strftime('%Y-%m-%d'),
            'quiz_score': round(avg_score, 1),
            'vocab_learned': day_vocab.count(),
            'lessons_completed': day_lessons.count()
        })
    
    # Reverse the list so it's in chronological order
    daily_progress.reverse()
    
    # Calculate overall stats
    total_quizzes = completed_quizzes.count()
    total_vocab = vocabulary_words.count()
    total_lessons = completed_lessons.count()
    
    # Calculate average quiz score
    if completed_quizzes.exists():
        overall_scores = []
        for quiz in completed_quizzes:
            score_percentage = (quiz.score / quiz.total_questions) * 100 if quiz.total_questions > 0 else 0
            overall_scores.append(score_percentage)
        avg_quiz_score = round(sum(overall_scores) / len(overall_scores), 1)
    else:
        avg_quiz_score = 0
    
    context = {
        'user': request.user,
        'posts': user_posts,
        'connections': user_connections,
        'completed_quizzes': completed_quizzes,
        'vocabulary_words': vocabulary_words,
        'completed_lessons': completed_lessons,
        'daily_progress': json.dumps(daily_progress),
        'daily_progress_raw': daily_progress,
        'total_quizzes': total_quizzes,
        'total_vocab': total_vocab,
        'total_lessons': total_lessons,
        'avg_quiz_score': avg_quiz_score,
    }
    return render(request, 'main_core/profile.html', context)

@login_required
def settings(request):
    if request.method == 'POST':
        if 'delete_account' in request.POST:
            # Delete the user's account
            user = request.user
            user.delete()
            messages.success(request, 'Your account has been successfully deleted.')
            return redirect('main_core:home')
            
        if 'download_data' in request.POST:
            # Handle data download
            response = HttpResponse(content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="user_data.json"'
            
            # Get user's learning data
            completed_quizzes = Quiz.objects.filter(user=request.user, completed=True)
            vocabulary_words = UserVocabulary.objects.filter(user=request.user)
            completed_lessons = UserLesson.objects.filter(user=request.user)
            
            # Calculate quiz statistics
            quiz_stats = []
            for quiz in completed_quizzes:
                quiz_stats.append({
                    'type': quiz.quiz_type,
                    'hsk_level': quiz.hsk_level,
                    'score': quiz.score,
                    'total_questions': quiz.total_questions,
                    'date': quiz.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                })
            
            # Prepare user data
            user_data = {
                'personal_info': {
                    'username': request.user.username,
                    'full_name': request.user.full_name,
                    'email': request.user.email,
                    'phone': request.user.phone,
                    'age': request.user.age,
                    'nationality': request.user.nationality,
                    'institute': request.user.institute,
                    'university_field': request.user.university_field,
                    'student_id': request.user.student_id,
                    'batch': request.user.batch,
                    'current_hsk_level': request.user.current_hsk_level,
                },
                'learning_progress': {
                    'points': request.user.points,
                    'completed_lessons': request.user.completed_lessons,
                    'learning_streak': request.user.learning_streak,
                    'quizzes': quiz_stats,
                    'vocabulary_words': [
                        {
                            'word': word.word.chinese,
                            'pinyin': word.word.pinyin,
                            'english': word.word.english,
                            'is_learned': word.is_learned,
                            'last_reviewed': word.last_reviewed.strftime('%Y-%m-%d %H:%M:%S') if word.last_reviewed else None,
                        } for word in vocabulary_words
                    ],
                    'completed_lessons': [
                        {
                            'lesson': lesson.lesson.grammar_id,
                            'completed_at': lesson.completed_at.strftime('%Y-%m-%d %H:%M:%S') if lesson.completed_at else None,
                        } for lesson in completed_lessons
                    ],
                }
            }
            
            json.dump(user_data, response, indent=4)
            return response
            
        form = UserSettingsForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('main_core:settings')
    else:
        form = UserSettingsForm(instance=request.user)
    
    return render(request, 'main_core/settings.html', {'form': form})

@login_required
def view_pdf(request, hsk_level):
    if not 1 <= hsk_level <= 6:
        raise Http404("Invalid HSK level")

    # Construct the absolute path to the PDF file
    pdf_filename = "textbook.pdf"
    pdf_path = os.path.join('C:', os.sep, 'Users', 'parve', 'Desktop', 'CHINAS LEGACY', 
                           'static', 'data', 'books', f'hsk{hsk_level}', pdf_filename)

    # Debug information
    print(f"Looking for PDF at: {pdf_path}")
    print(f"File exists: {os.path.exists(pdf_path)}")

    if not os.path.exists(pdf_path):
        raise Http404(f"PDF file not found for HSK {hsk_level}. Please ensure the file exists at: {pdf_path}")

    # Open and stream the PDF file
    try:
        pdf_file = open(pdf_path, 'rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=HSK{hsk_level}_textbook.pdf'
        return response
    except Exception as e:
        raise Http404(f"Error opening PDF file: {str(e)}")

@login_required
def inbox(request):
    # Get user's connections
    connections = UserConnection.objects.filter(
        (models.Q(user=request.user) | models.Q(connected_to=request.user)),
        status='accepted'
    ).select_related('user', 'connected_to')
    
    # Keep track of processed users to avoid duplicates
    processed_users = set()
    connection_users = []
    
    for conn in connections:
        # Determine which user is the connection
        other_user = conn.connected_to if conn.user == request.user else conn.user
        
        # Skip if we've already processed this user
        if other_user.id in processed_users:
            continue
        
        processed_users.add(other_user.id)
        
        # Get the last message between users
        last_message = Message.objects.filter(
            (models.Q(sender=request.user, receiver=other_user) |
             models.Q(sender=other_user, receiver=request.user))
        ).order_by('-created_at').first()
        
        # Get unread message count
        unread_count = Message.objects.filter(
            sender=other_user,
            receiver=request.user,
            is_read=False
        ).count()
        
        # Add user info with last message
        user_info = {
            'id': other_user.id,
            'username': other_user.username,
            'last_message': last_message.content if last_message else None,
            'last_message_time': last_message.created_at if last_message else None,
            'unread_count': unread_count,
            'is_online': other_user.last_login and (timezone.now() - other_user.last_login).seconds < 300  # Online if active in last 5 minutes
        }
        connection_users.append(user_info)
    
    # Sort connections by last message time, putting users with unread messages first
    min_time = timezone.make_aware(datetime.min)
    
    connection_users.sort(key=lambda x: (
        -x['unread_count'],  # Sort by unread count (descending)
        x['last_message_time'] or min_time  # Then by last message time
    ), reverse=True)
    
    return render(request, 'main_core/inbox.html', {
        'connections': connection_users
    })

@login_required
def get_chat_messages(request, user_id):
    try:
        # Get the other user
        other_user = CustomUser.objects.get(id=user_id)
        
        # Check if there's a connection
        connection_exists = UserConnection.objects.filter(
            (models.Q(user=request.user, connected_to=other_user) |
             models.Q(user=other_user, connected_to=request.user)),
            status='accepted'
        ).exists()
        
        if not connection_exists:
            return JsonResponse({
                'status': 'error',
                'message': 'No connection exists'
            }, status=403)
        
        # Get the after_id from query params
        after_id = request.GET.get('after')
        
        # Base query for messages
        messages = Message.objects.select_related('sender', 'receiver').filter(
            (models.Q(sender=request.user, receiver=other_user) |
             models.Q(sender=other_user, receiver=request.user))
        )
        
        # If after_id is provided, only get messages after that ID
        if after_id:
            try:
                after_id = int(after_id)
                messages = messages.filter(id__gt=after_id)
            except (ValueError, TypeError):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid after_id parameter'
                }, status=400)
        
        messages = messages.order_by('created_at')
        
        # Mark received messages as read
        unread_messages = messages.filter(receiver=request.user, is_read=False)
        if unread_messages.exists():
            unread_messages.update(is_read=True)
            Notification.objects.filter(
                user=request.user,
                message__in=unread_messages,
                notification_type='message'
            ).update(is_read=True)
        
        # Format messages for response
        messages_data = [{
            'id': msg.id,
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
            'sender': {
                'id': msg.sender.id,
                'username': msg.sender.username
            },
            'receiver': {
                'id': msg.receiver.id,
                'username': msg.receiver.username
            },
            'is_read': msg.is_read
        } for msg in messages]
        
        return JsonResponse({
            'status': 'success',
            'messages': messages_data,
            'user': {
                'id': other_user.id,
                'username': other_user.username,
                'is_online': other_user.last_login and (timezone.now() - other_user.last_login).seconds < 300
            }
        })
        
    except CustomUser.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error in get_chat_messages: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while loading messages'
        }, status=500)

@login_required
def send_message(request, receiver_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Message content is required'})
        
        # Get receiver
        receiver = CustomUser.objects.get(id=receiver_id)
        
        # Check if there's a connection
        connection_exists = UserConnection.objects.filter(
            (models.Q(user=request.user, connected_to=receiver) |
             models.Q(user=receiver, connected_to=request.user)),
            status='accepted'
        ).exists()
        
        if not connection_exists:
            return JsonResponse({'status': 'error', 'message': 'No connection exists'})
        
        # Create message
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content
        )
        
        # Create notification
        Notification.objects.create(
            user=receiver,
            notification_type='message',
            sender=request.user,
            message=message
        )
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.content,
                'created_at': message.created_at.isoformat(),
                'sender': {
                    'id': message.sender.id,
                    'username': message.sender.username
                },
                'receiver': {
                    'id': message.receiver.id,
                    'username': message.receiver.username
                },
                'is_read': message.is_read
            }
        })
        
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def mark_message_read(request, message_id):
    try:
        message = Message.objects.get(id=message_id, receiver=request.user)
        message.is_read = True
        message.save()
        
        # Mark associated notification as read
        Notification.objects.filter(
            user=request.user,
            message=message,
            notification_type='message'
        ).update(is_read=True)
        
        return JsonResponse({'status': 'success'})
    except Message.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Message not found'})

@login_required
def send_friend_request(request, user_id):
    if request.method == 'POST':
        try:
            to_user = CustomUser.objects.get(id=user_id)
            
            # Check if request already exists
            if UserConnection.objects.filter(
                user=request.user,
                connected_to=to_user
            ).exists():
                return JsonResponse({'status': 'error', 'message': 'Friend request already exists'})
            
            # Create connection request
            UserConnection.objects.create(
                user=request.user,
                connected_to=to_user,
                status='pending'
            )
            
            return JsonResponse({'status': 'success', 'message': 'Friend request sent'})
            
        except CustomUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def accept_friend_request(request, request_id):
    if request.method == 'POST':
        try:
            connection = UserConnection.objects.get(
                id=request_id,
                connected_to=request.user,
                status='pending'
            )
            connection.status = 'accepted'
            connection.save()
            
            # Create reverse connection
            UserConnection.objects.create(
                user=request.user,
                connected_to=connection.user,
                status='accepted'
            )
            
            return JsonResponse({'status': 'success', 'message': 'Friend request accepted'})
            
        except UserConnection.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Friend request not found'})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def decline_friend_request(request, request_id):
    if request.method == 'POST':
        try:
            connection = UserConnection.objects.get(
                id=request_id,
                connected_to=request.user,
                status='pending'
            )
            connection.status = 'declined'
            connection.save()
            return JsonResponse({'status': 'success', 'message': 'Friend request declined'})
        except UserConnection.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Friend request not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def pinyin_chart(request):
    """Pinyin chart view."""
    return render(request, 'main_core/pinyin_chart.html')

def test_deepseek(request):
    """Test view for DeepSeek API integration."""
    try:
        # Test with a simple grammar point
        explanation = deepseek_api.get_grammar_explanation(
            title="Using 在 (zài)",
            pattern="Subject + 在 + Verb + Object",
            example="我在学习中文。(Wǒ zài xuéxí zhōngwén.) - I am studying Chinese.",
            language='en'
        )
        
        return JsonResponse({
            'status': 'success',
            'explanation': explanation
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def retry_explanation(request, lesson_id):
    """Generate a new explanation for a grammar lesson."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        lesson = get_object_or_404(GrammarLesson, id=lesson_id)
        language = getattr(request, 'LANGUAGE_CODE', 'en')
        
        logger.info(f"Generating explanation for lesson {lesson_id} in {language}")
        
        # Initialize DeepSeek API
        api = DeepSeekAPI()
        
        # Get detailed explanation
        explanation = api.get_grammar_explanation(
            title=lesson.title,
            pattern=lesson.pattern,
            example=lesson.example,
            language=language
        )
        
        if not explanation:
            logger.error(f"Empty explanation received for lesson {lesson_id}")
            return JsonResponse({
                'status': 'error',
                'message': _('explanation_error_message')
            }, status=500)
        
        # Validate explanation format
        required_sections = ['detailed_explanation', 'usage_notes', 'additional_examples', 'common_mistakes']
        if not all(section in explanation and explanation[section] for section in required_sections):
            logger.error(f"Incomplete explanation received for lesson {lesson_id}")
            return JsonResponse({
                'status': 'error',
                'message': _('explanation_error_message')
            }, status=500)
        
        logger.info(f"Successfully generated explanation for lesson {lesson_id}")
        return JsonResponse({
            'status': 'success',
            'explanation': explanation
        })
        
    except GrammarLesson.DoesNotExist:
        logger.error(f"Lesson {lesson_id} not found")
        return JsonResponse({
            'status': 'error',
            'message': _('lesson_not_found')
        }, status=404)
    except ValueError as e:
        logger.error(f"API error for lesson {lesson_id}: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error for lesson {lesson_id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': _('explanation_error_message')
        }, status=500)

@login_required
def download_user_data(request, format='json'):
    """Download user data in JSON or CSV format."""
    user = request.user
    
    # Prepare user data
    user_data = {
        'Personal Information': {
            'Username': user.username,
            'Email': user.email,
            'Full Name': user.full_name,
            'Age': user.age,
            'Nationality': user.nationality,
            'Phone': user.phone,
        },
        'Academic Information': {
            'Institute': user.institute,
            'Field of Study': user.university_field,
            'Batch': user.batch,
            'Student ID': user.student_id,
        },
        'Chinese Proficiency': {
            'Current HSK Level': user.current_hsk_level,
            'Learning Streak': user.learning_streak,
            'Points': user.points,
            'Completed Lessons': user.completed_lessons,
        },
        'Learning Statistics': {
            'Completed Quizzes': user.quiz_set.filter(completed=True).count(),
            'Vocabulary Words': user.uservocabulary_set.filter(is_learned=True).count(),
            'Grammar Lessons': user.userlesson_set.filter(is_completed=True).count(),
        }
    }
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="user_data_{timestamp}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Category', 'Field', 'Value'])
        
        for category, fields in user_data.items():
            for field, value in fields.items():
                writer.writerow([category, field, value])
                
        return response
    else:  # JSON format
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="user_data_{timestamp}.json"'
        json.dump(user_data, response, indent=2)
        return response
