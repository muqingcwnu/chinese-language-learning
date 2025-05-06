from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TimelinePost, Comment

# Add your signal handlers here if needed
# For example:
@receiver(post_save, sender=TimelinePost)
def handle_timeline_post_save(sender, instance, created, **kwargs):
    pass

@receiver(post_save, sender=Comment)
def handle_comment_save(sender, instance, created, **kwargs):
    pass