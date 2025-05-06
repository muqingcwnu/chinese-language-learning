import os
import requests
import urllib3
from decouple import config

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_to_file(message):
    with open('api_debug.txt', 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def test_api():
    print_to_file('\n=== Starting API Test ===\n')
    
    # Get API key and verify it
    api_key = config('DEEPSEEK_API_KEY')
    print_to_file(f'API Key (first 8 chars): {api_key[:8]}')
    
    # Set up request parameters
    url = 'https://api.deepseek.ai/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {
                'role': 'user',
                'content': '你好'
            }
        ]
    }
    
    print_to_file(f'\nURL: {url}')
    print_to_file(f'Headers: {headers}')
    print_to_file(f'Payload: {payload}')
    
    try:
        print_to_file('\nMaking API request...')
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            verify=False,
            timeout=30
        )
        
        print_to_file(f'\nStatus Code: {response.status_code}')
        print_to_file(f'Response Headers: {dict(response.headers)}')
        print_to_file(f'Response Body: {response.text}')
        
    except requests.exceptions.RequestException as e:
        print_to_file(f'\nRequest Error: {str(e)}')
    except Exception as e:
        print_to_file(f'\nUnexpected Error: {str(e)}')

def test_direct_connection():
    """Test direct connection to DeepSeek API with minimal dependencies"""
    api_key = config('DEEPSEEK_API_KEY')
    
    # Test endpoints
    endpoints = [
        "http://34.107.189.223/v1/chat/completions",
        "http://52.58.133.175/v1/chat/completions",
        "http://api.deepseek.ai/v1/chat/completions"
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Test connection"}
        ],
        "max_tokens": 5
    }
    
    print("Testing Direct Connections...")
    print("=" * 50)
    
    for endpoint in endpoints:
        print(f"\nTrying endpoint: {endpoint}")
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=10,
                verify=False
            )
            
            print(f"Status Code: {response.status_code}")
            if response.ok:
                print("Success!")
                print("Response:", response.json())
                return True
            else:
                print("Error:", response.text)
                
        except requests.exceptions.RequestException as e:
            print(f"Connection failed: {str(e)}")
    
    return False

if __name__ == "__main__":
    test_api()
    success = test_direct_connection()
    print("\nFinal Result:", "Success" if success else "All connection attempts failed")