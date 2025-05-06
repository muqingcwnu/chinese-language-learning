"""
Utility class for interacting with the DeepSeek API using OpenAI SDK.
"""

import os
import json
from typing import Dict, Any, Optional, Tuple, List
from decouple import config
import logging
import time
from openai import OpenAI
from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepSeekAPI:
    """A class to handle interactions with the DeepSeek API using OpenAI SDK."""
    
    def __init__(self):
        """Initialize the DeepSeek API client."""
        self.api_key = settings.DEEPSEEK_API_KEY
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1"
        )
        self.model = "deepseek-chat"

    def test_connection(self) -> Tuple[bool, str]:
        """Test the connection to the DeepSeek API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=50
            )
            return True, "Connection successful"
        except Exception as e:
            logger.error(f"API connection error: {str(e)}")
            return False, f"Connection failed: {str(e)}"

    def generate_response(self, user_message: str) -> str:
        """Generate a response to a user message.
        
        Args:
            user_message: The message from the user
            
        Returns:
            str: The generated response or error message
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful Chinese language learning assistant. You can help with translations, grammar explanations, and general language learning questions. Always provide explanations in both English and Chinese when appropriate."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"

    def get_grammar_explanation(self, title: str, pattern: str, example: str, language: str = 'en') -> Dict[str, Any]:
        """Get an explanation for a grammar point."""
        try:
            prompt = self._construct_grammar_prompt(title, pattern, example, language)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Chinese language expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            explanation = response.choices[0].message.content
            return self._parse_grammar_response(explanation)
        except Exception as e:
            logger.error(f"Error getting grammar explanation: {str(e)}")
            return {
                "error": True,
                "message": str(e)
            }

    def _construct_grammar_prompt(self, title: str, pattern: str, example: str, language: str) -> str:
        """Construct the prompt for grammar explanation."""
        if language == 'zh':
            return f"""请解释以下中文语法点：
标题：{title}
语法规则：{pattern}
例句：{example}

请提供以下格式的解释：
1. 详细解释
2. 使用说明
3. 更多例子
4. 常见错误"""
        else:
            return f"""Please explain the following Chinese grammar point:
Title: {title}
Pattern: {pattern}
Example: {example}

Please provide the explanation in the following format:
1. Detailed Explanation
2. Usage Notes
3. Additional Examples
4. Common Mistakes"""

    def _parse_grammar_response(self, response: str) -> Dict[str, Any]:
        """Parse the API response into structured data."""
        try:
            sections = response.split('\n\n')
            explanation = {
                "detailed_explanation": "",
                "usage_notes": "",
                "additional_examples": "",
                "common_mistakes": "",
                "error": False
            }
            
            current_section = "detailed_explanation"
            for section in sections:
                if "Usage Notes" in section or "使用说明" in section:
                    current_section = "usage_notes"
                elif "Additional Examples" in section or "更多例子" in section:
                    current_section = "additional_examples"
                elif "Common Mistakes" in section or "常见错误" in section:
                    current_section = "common_mistakes"
                
                explanation[current_section] += section + "\n"
            
            return explanation
        except Exception as e:
            logger.error(f"Error parsing grammar response: {str(e)}")
            return {
                "error": True,
                "message": f"Failed to parse response: {str(e)}"
            }

    def generate_vocab_options(self, chinese: str, pinyin: str, english: str) -> List[str]:
        """Generate incorrect but plausible options for vocabulary quiz.
        
        Args:
            chinese: The Chinese word/character
            pinyin: The pinyin pronunciation
            english: The correct English translation
            
        Returns:
            List[str]: List of 3 incorrect but plausible English translations
        """
        try:
            prompt = f"""Generate 3 incorrect but plausible English translations for the Chinese word '{chinese}' ({pinyin}).
Current meaning: {english}
Format your response as a simple list with one option per line.
The options should be related but clearly different from the correct meaning."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Chinese language teaching assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            # Parse the response to get the options
            options_text = response.choices[0].message.content.strip()
            options = [opt.strip() for opt in options_text.split('\n') if opt.strip()]
            
            # Ensure we have exactly 3 options
            if len(options) < 3:
                logger.warning(f"Not enough options generated for {chinese}. Adding generic options.")
                default_options = ["teacher", "book", "school", "person", "thing"]
                while len(options) < 3:
                    option = default_options[len(options)]
                    if option != english and option not in options:
                        options.append(option)
            
            return options[:3]  # Return exactly 3 options
            
        except Exception as e:
            logger.error(f"Error generating vocabulary options for {chinese}: {str(e)}")
            # Return generic incorrect options as fallback
            return ["teacher", "book", "school"]

    def generate_grammar_questions(self, hsk_level: int, num_questions: int) -> List[Dict[str, Any]]:
        """Generate grammar questions for a quiz.
        
        Args:
            hsk_level: The HSK level (1-6)
            num_questions: Number of questions to generate
            
        Returns:
            List[Dict]: List of questions with text, correct answer, and incorrect options
        """
        try:
            prompt = f"""Generate {num_questions} Chinese grammar questions for HSK level {hsk_level}.
For each question, provide:
1. A grammar question in English
2. The correct Chinese answer
3. Three incorrect Chinese answers
Format each question as a JSON object."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Chinese language teaching assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response to get the questions
            questions_text = response.choices[0].message.content.strip()
            try:
                questions = json.loads(questions_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract questions manually
                questions = []
                current_question = {}
                for line in questions_text.split('\n'):
                    if 'Question' in line:
                        if current_question:
                            questions.append(current_question)
                        current_question = {'question_text': line.strip()}
                    elif 'Correct' in line:
                        current_question['correct_answer'] = line.replace('Correct:', '').strip()
                    elif 'Incorrect' in line:
                        if 'incorrect_options' not in current_question:
                            current_question['incorrect_options'] = []
                        current_question['incorrect_options'].append(line.replace('Incorrect:', '').strip())
                if current_question:
                    questions.append(current_question)
            
            return questions[:num_questions]
            
        except Exception as e:
            logger.error(f"Error generating grammar questions for HSK{hsk_level}: {str(e)}")
            return []

    def generate_sentence_questions(self, hsk_level: int, num_questions: int) -> List[Dict[str, Any]]:
        """Generate sentence rearrangement questions for a quiz.
        
        Args:
            hsk_level: The HSK level (1-6)
            num_questions: Number of questions to generate
            
        Returns:
            List[Dict]: List of questions with original sentence, scrambled words, pinyin, and English translation
        """
        try:
            prompt = f"""Generate {num_questions} Chinese sentence rearrangement questions for HSK level {hsk_level}.
For each sentence, provide:
1. The original Chinese sentence
2. The sentence split into individual words
3. The pinyin pronunciation
4. The English translation
Format each sentence as a JSON object."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Chinese language teaching assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response to get the sentences
            sentences_text = response.choices[0].message.content.strip()
            try:
                sentences = json.loads(sentences_text)
                for sentence in sentences:
                    # Scramble the words
                    words = sentence['original_sentence'].split()
                    import random
                    random.shuffle(words)
                    sentence['scrambled_words'] = words
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract sentences manually
                sentences = []
                current_sentence = {}
                for line in sentences_text.split('\n'):
                    if 'Sentence' in line:
                        if current_sentence:
                            sentences.append(current_sentence)
                        current_sentence = {}
                    elif 'Chinese:' in line:
                        current_sentence['original_sentence'] = line.replace('Chinese:', '').strip()
                        # Scramble the words
                        words = current_sentence['original_sentence'].split()
                        import random
                        random.shuffle(words)
                        current_sentence['scrambled_words'] = words
                    elif 'Pinyin:' in line:
                        current_sentence['pinyin'] = line.replace('Pinyin:', '').strip()
                    elif 'English:' in line:
                        current_sentence['english_translation'] = line.replace('English:', '').strip()
                if current_sentence:
                    sentences.append(current_sentence)
            
            return sentences[:num_questions]
            
        except Exception as e:
            logger.error(f"Error generating sentence questions for HSK{hsk_level}: {str(e)}")
            return []

# Create a singleton instance
deepseek_api = DeepSeekAPI()