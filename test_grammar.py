from openai import OpenAI
import os
import sys
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_grammar_explanation():
    """Test the grammar explanation functionality."""
    api_key = 'sk-93e72b6c6cc0453ca63ed6cf777a4c99'
    base_url = 'https://api.deepseek.com/v1'
    
    try:
        logger.info("Initializing OpenAI client...")
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Test data
        title = "把 (bǎ) Structure"
        pattern = "Subject + 把 + Object + Verb + Complement"
        example = "我把房间打扫干净了。(Wǒ bǎ fángjiān dǎsǎo gānjìng le.) - I cleaned the room."
        
        logger.info("Sending grammar explanation request...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a Chinese language expert."},
                {"role": "user", "content": f"""Please explain the following Chinese grammar point:
Title: {title}
Pattern: {pattern}
Example: {example}

Please provide the explanation in the following format:
1. Detailed Explanation
2. Usage Notes
3. Additional Examples
4. Common Mistakes"""}
            ],
            max_tokens=1000
        )
        
        if response and response.choices:
            explanation = response.choices[0].message.content
            logger.info("Grammar explanation received successfully!")
            logger.info("\nGrammar Explanation:")
            print("\n" + explanation)
            return True, "Grammar explanation generated successfully"
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False, f"Failed to get grammar explanation: {str(e)}"

if __name__ == "__main__":
    success, message = test_grammar_explanation()
    print(f"\nSuccess: {success}")
    print(f"Message: {message}") 