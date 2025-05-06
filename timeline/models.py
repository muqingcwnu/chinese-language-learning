from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

class TimelinePost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='timeline_posts/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    shares = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_posts', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s post at {self.created_at}"

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    def get_like_count(self):
        return self.likes.count()

    def get_share_count(self):
        return self.shares.count()

class Comment(models.Model):
    post = models.ForeignKey(TimelinePost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post}'
