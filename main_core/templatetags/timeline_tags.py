from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using bracket notation."""
    return dictionary.get(key)

@register.simple_tag
def get_reaction_choices():
    """Return a list of reaction choices with their emojis."""
    return [
        ('like', '👍'),
        ('love', '❤️'),
        ('haha', '😄'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😠'),
    ]

@register.filter
@stringfilter
def highlight_mentions(value):
    """Highlight @mentions in text."""
    import re
    pattern = r'@(\w+)'
    return re.sub(pattern, r'<span class="text-red-600">@\1</span>', value) 