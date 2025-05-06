import sys
import os
import django
from datetime import datetime

try:
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    print("Django environment setup successful")
except Exception as e:
    print(f"Failed to set up Django environment: {str(e)}")
    sys.exit(1)

try:
    from utils.deepseek_api import deepseek_api
    print("Successfully imported deepseek_api")
except Exception as e:
    print(f"Failed to import deepseek_api: {str(e)}")
    sys.exit(1)

def test_vocab_quiz():
    try:
        print("\nTesting Vocabulary Quiz Generation:")
        print("-" * 50)
        
        word = "学生"
        pinyin = "xuéshēng"
        english = "student"
        
        print(f"Word: {word} ({pinyin}) - {english}")
        options = deepseek_api.generate_vocab_options(word, pinyin, english)
        print("\nGenerated incorrect options:")
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")
        return True
    except Exception as e:
        print(f"Error in vocab quiz test: {str(e)}")
        return False

def test_grammar_quiz():
    try:
        print("\nTesting Grammar Quiz Generation:")
        print("-" * 50)
        
        questions = deepseek_api.generate_grammar_questions(1, 2)
        print(f"\nGenerated {len(questions)} grammar questions:")
        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}:")
            print(f"Text: {q['question_text']}")
            print(f"Correct: {q['correct_answer']}")
            print("Incorrect options:")
            for opt in q['incorrect_options']:
                print(f"- {opt}")
        return True
    except Exception as e:
        print(f"Error in grammar quiz test: {str(e)}")
        return False

def test_sentence_quiz():
    try:
        print("\nTesting Sentence Quiz Generation:")
        print("-" * 50)
        
        sentences = deepseek_api.generate_sentence_questions(1, 2)
        print(f"\nGenerated {len(sentences)} sentence questions:")
        for i, s in enumerate(sentences, 1):
            print(f"\nSentence {i}:")
            print(f"Original: {s['original_sentence']}")
            print(f"Scrambled: {', '.join(s['scrambled_words'])}")
            print(f"Pinyin: {s['pinyin']}")
            print(f"English: {s['english_translation']}")
        return True
    except Exception as e:
        print(f"Error in sentence quiz test: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting Quiz Tests at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 50)
    
    success = True
    
    # Run each test and track success
    if not test_vocab_quiz():
        success = False
    if not test_grammar_quiz():
        success = False
    if not test_sentence_quiz():
        success = False
    
    print("\nTest Summary:")
    if success:
        print("All tests completed successfully!")
    else:
        print("Some tests failed. Check the output above for details.")
    
    print("\nTest run completed at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 