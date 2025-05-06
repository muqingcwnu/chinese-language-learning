from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using bracket notation."""
    if dictionary is None:
        return None
    # Convert string key to integer if possible
    try:
        if isinstance(key, str):
            key = int(key)
    except (ValueError, TypeError):
        pass
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    """Multiply the arg and value"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0 