from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def format_bullets(value):
    """
    Convert bullet points (•) to HTML list items and add HTML formatting.
    Also converts **text** to bold formatting.
    """
    if not value:
        return value
    
    # Convert markdown-style bold (**text**) to HTML bold
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', value)
    
    # Split by bullet points and create HTML list
    lines = formatted.split('\n')
    html_lines = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('•'):
            # Remove bullet and wrap in list item
            content = line[1:].strip()
            html_lines.append(f'<li>{content}</li>')
        elif line.startswith('-'):
            # Handle dash bullets too
            content = line[1:].strip()
            html_lines.append(f'<li>{content}</li>')
        elif line:
            # Non-bullet line, just add as paragraph if not empty
            html_lines.append(f'<p>{line}</p>')
    
    # Wrap consecutive list items in ul tags
    result = []
    in_list = False
    
    for line in html_lines:
        if line.startswith('<li>'):
            if not in_list:
                result.append('<ul class="mb-0">')
                in_list = True
            result.append(line)
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)
    
    if in_list:
        result.append('</ul>')
    
    return mark_safe(''.join(result))

@register.filter
def format_bold(value):
    """
    Convert **text** to HTML bold formatting
    """
    if not value:
        return value
    
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', value)
    return mark_safe(formatted)