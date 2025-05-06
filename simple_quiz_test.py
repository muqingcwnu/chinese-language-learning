from openai import OpenAI
import os
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set API key directly
API_KEY = "sk-467710c038f1445e8bc30c4245d7ad92"

# Initialize OpenAI client with DeepSeek configuration
client = OpenAI(
    api_key=API_KEY,
    base_url="http://34.107.189.223/v1"  # Using the working endpoint from minimal_test.py
)

def test_quiz_generation():
    print("Testing Quiz Generation...")
    
    try:
        # Test vocabulary quiz
        print("\n1. Testing vocabulary quiz generation...")
        vocab_prompt = """Generate 3 incorrect but plausible English translations for the Chinese word '学生' (xuéshēng).
Current meaning: student
Format your response as a simple list with one option per line."""

        vocab_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a Chinese language teaching assistant."},
                {"role": "user", "content": vocab_prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        print("Vocabulary options generated:", vocab_response.choices[0].message.content)

        # Test grammar quiz
        print("\n2. Testing grammar quiz generation...")
        grammar_prompt = """Generate 1 HSK1 level grammar question with:
1. A grammar question in English
2. The correct Chinese answer
3. Three incorrect Chinese answers"""

        grammar_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a Chinese language teaching assistant."},
                {"role": "user", "content": grammar_prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        print("Grammar question generated:", grammar_response.choices[0].message.content)

        print("\nAll tests completed successfully!")
        return True

    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_quiz_generation()
    print("\nTest Status:", "Success" if success else "Failed") 