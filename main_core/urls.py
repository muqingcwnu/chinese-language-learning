from django.urls import path
from . import views

app_name = 'main_core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
    
    # Grammar URLs
    path('grammar/', views.grammar_home, name='grammar_home'),
    path('grammar/level/<int:level>/', views.grammar_level, name='grammar_level'),
    path('grammar/category/<str:category>/', views.grammar_category, name='grammar_category'),
    path('grammar/lesson/<int:lesson_id>/', views.grammar_lesson, name='grammar_lesson'),
    path('grammar/lesson/<int:lesson_id>/toggle-completed/', views.toggle_lesson_completed, name='toggle_lesson_completed'),
    path('grammar/lesson/<int:lesson_id>/explanation/', views.retry_explanation, name='retry_explanation'),
    
    # Lessons URLs
    path('lessons/', views.lessons_home, name='lessons_home'),
    path('lessons/book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('lessons/book/<int:book_id>/chapter/<int:chapter_number>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/pdf/<int:hsk_level>/', views.view_pdf, name='view_pdf'),
    
    # Tasks and Quiz URLs
    path('tasks/', views.tasks_home, name='tasks_home'),
    path('quiz/', views.quiz_home, name='quiz_home'),
    path('quiz/start/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
    path('quiz/history/', views.quiz_history, name='quiz_history'),
    
    # Timeline URLs
    path('timeline/', views.timeline_home, name='timeline_home'),
    path('timeline/post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('timeline/post/<int:post_id>/react/', views.add_reaction, name='add_reaction'),
    
    # User Connections URLs
    path('connections/', views.user_connections, name='user_connections'),
    path('connections/connect/<int:user_id>/', views.connect_user, name='connect_user'),
    path('connections/handle/<int:connection_id>/', views.handle_connection_request, name='handle_connection_request'),
    path('connections/remove/<int:connection_id>/', views.remove_connection, name='remove_connection'),
    
    # User Profile URLs
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('change-language/', views.change_language, name='change_language'),

    # Messaging and Friend Request URLs
    path('inbox/', views.inbox, name='inbox'),
    path('api/messages/<int:user_id>/', views.get_chat_messages, name='get_chat_messages'),
    path('send-message/<int:receiver_id>/', views.send_message, name='send_message'),
    path('mark-message-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
    path('send-friend-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline-friend-request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('handle-connection-request/<int:connection_id>/', views.handle_connection_request, name='handle_connection_request'),
    path('pinyin-chart/', views.pinyin_chart, name='pinyin_chart'),
    path('test/deepseek/', views.test_deepseek, name='test_deepseek'),
    path('profile/download/json/', views.download_user_data, name='download_user_data_json'),
    path('profile/download/csv/', views.download_user_data, {'format': 'csv'}, name='download_user_data_csv'),
] 