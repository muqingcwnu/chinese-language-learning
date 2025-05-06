import requests
from django.conf import settings
import json

def get_grammar_explanation(grammar_lesson, language='en'):
    """
    Get detailed grammar explanation from DeepSeek API.
    
    Args:
        grammar_lesson: GrammarLesson instance
        language: 'en' for English or 'zh' for Chinese
    
    Returns:
        dict: Contains detailed explanation, usage notes, and additional examples
    """
    try:
        # Prepare the prompt based on the language
        if language == 'zh':
            prompt = f"""请详细解释以下中文语法点：

语法点：{grammar_lesson.title_zh}
语法结构：{grammar_lesson.pattern_zh}
示例：{grammar_lesson.example_zh}

请提供：
1. 详细解释
2. 使用注意事项
3. 三个额外的例句
4. 常见错误
"""
        else:
            prompt = f"""Please explain the following Chinese grammar point in detail:

Grammar Point: {grammar_lesson.title_en}
Pattern: {grammar_lesson.pattern_en}
Example: {grammar_lesson.example_en}

Please provide:
1. Detailed explanation
2. Usage notes
3. Three additional examples
4. Common mistakes
"""

        # Call DeepSeek API
        headers = {
            'Authorization': f'Bearer {settings.DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json',
        }
        
        data = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 1000
        }
        
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            explanation = result['choices'][0]['message']['content']
            
            # Parse the explanation into sections
            sections = explanation.split('\n\n')
            parsed_explanation = {
                'detailed_explanation': sections[0] if len(sections) > 0 else '',
                'usage_notes': sections[1] if len(sections) > 1 else '',
                'additional_examples': sections[2] if len(sections) > 2 else '',
                'common_mistakes': sections[3] if len(sections) > 3 else ''
            }
            
            return parsed_explanation
        else:
            return {
                'error': f'API Error: {response.status_code}',
                'detailed_explanation': 'Unable to fetch explanation at this time.',
                'usage_notes': '',
                'additional_examples': '',
                'common_mistakes': ''
            }
            
    except Exception as e:
        return {
            'error': str(e),
            'detailed_explanation': 'Unable to fetch explanation at this time.',
            'usage_notes': '',
            'additional_examples': '',
            'common_mistakes': ''
        } 