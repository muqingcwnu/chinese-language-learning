from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using bracket notation."""
    return dictionary.get(key)

@register.simple_tag(takes_context=True)
def trans(context, key):
    """Translate text based on current language."""
    try:
        from main_core.translations import TRANSLATIONS
        current_lang = context.get('LANGUAGE', 'en')
        translation = TRANSLATIONS.get(key, {}).get(current_lang, key)
        return mark_safe(translation)
    except Exception:
        return key

@register.filter
@stringfilter
def highlight_mentions(value):
    """Highlight @mentions in text."""
    import re
    pattern = r'@(\w+)'
    return re.sub(pattern, r'<span class="text-red-600">@\1</span>', value)

@register.simple_tag(takes_context=True)
def get_current_language(context):
    """Return the name of the current language."""
    current_lang = context.get('LANGUAGE', 'en')
    return '中文' if current_lang == 'zh' else 'English'

@register.simple_tag(takes_context=True)
def get_language_code(context):
    """Return the current language code in uppercase."""
    return context.get('LANGUAGE', 'en').upper()