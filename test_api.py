from openai import OpenAI
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_api():
    """Test the DeepSeek API connection using the OpenAI SDK."""
    api_key = 'sk-93e72b6c6cc0453ca63ed6cf777a4c99'
    base_url = 'https://api.deepseek.com/v1'
    
    try:
        logger.info(f"Testing API connection with key: {api_key[:8]}...")
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ],
            max_tokens=50
        )
        
        if response and response.choices:
            logger.info("API connection successful!")
            logger.info(f"Response: {response.choices[0].message.content}")
            return True, "Connection successful"
    except Exception as e:
        logger.error(f"API connection error: {str(e)}")
        return False, f"Connection failed: {str(e)}"

if __name__ == "__main__":
    success, message = test_api()
    print(f"Success: {success}")
    print(f"Message: {message}") 