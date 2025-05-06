"""
Configuration settings for the DeepSeek API integration.
"""

from django.conf import settings

# API Configuration
API_KEY = settings.DEEPSEEK_API_KEY
API_ENDPOINT = 'https://api.deepseek.com/v1/chat/completions'  # Replace with actual endpoint
MODEL = 'deepseek-chat'  # Replace with actual model name

# Prompt Templates
GRAMMAR_EXPLANATION_PROMPT = {
    'en': """
Please provide a detailed explanation of the following Chinese grammar point:

Title: {title}
Pattern: {pattern}
Example: {example}

Please include:
1. A detailed explanation of how this grammar pattern works
2. Key usage notes and restrictions
3. Additional examples showing different contexts
4. Common mistakes to avoid
""",
    'zh': """
请详细解释以下中文语法点：

标题：{title}
语法模式：{pattern}
例句：{example}

请包含：
1. 详细说明此语法模式如何使用
2. 重要的使用注意事项和限制
3. 展示不同语境的额外例子
4. 常见错误提醒
"""
}

# Response Structure
RESPONSE_STRUCTURE = {
    'detailed_explanation': '',
    'usage_notes': [],
    'additional_examples': [],
    'common_mistakes': []
} 