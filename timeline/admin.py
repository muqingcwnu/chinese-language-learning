from django.contrib import admin
from .models import TimelinePost, Comment

@admin.register(TimelinePost)
class TimelinePostAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at', 'get_like_count', 'get_share_count')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'user__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'content', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
