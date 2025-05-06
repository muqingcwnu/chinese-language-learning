from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    like_post,
    share_post,
    add_comment,
    delete_comment,
)

app_name = 'timeline'

urlpatterns = [
    path('', PostListView.as_view(), name='timeline-home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/like/', like_post, name='post-like'),
    path('post/<int:pk>/share/', share_post, name='post-share'),
    path('post/<int:pk>/comment/', add_comment, name='add-comment'),
    path('comment/<int:pk>/delete/', delete_comment, name='delete-comment'),
]