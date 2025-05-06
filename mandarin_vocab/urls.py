from django.urls import path
from . import views

app_name = 'mandarin_vocab'

urlpatterns = [
    path('', views.vocab_home, name='vocab_home'),
    path('hsk/<int:level>/', views.hsk_level, name='hsk_level'),
    path('word/<int:word_id>/', views.word_detail, name='word_detail'),
    path('my-vocabulary/', views.my_vocabulary, name='my_vocabulary'),
    path('books/', views.books, name='books'),
    path('api/toggle-learned/<int:word_id>/', views.toggle_learned, name='toggle_learned'),
    path('api/get-audio/<int:word_id>/', views.get_audio, name='get_audio'),
] 