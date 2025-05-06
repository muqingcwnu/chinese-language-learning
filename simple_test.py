import requests
from decouple import config
import json
from datetime import datetime
import os
import sys
import traceback

try:
    # Print startup message
    print("Starting API test...")
    
    # Test internet connectivity first
    print("Testing internet connection...")
    response = requests.get('https://www.google.com', timeout=5)
    print(f"Internet connection test: OK (Status {response.status_code})")
    
    # Load API key
    print("\nLoading API key...")
    api_key = config('DEEPSEEK_API_KEY')
    print("API key loaded successfully")
    
    # Basic test request
    url = 'http://34.107.189.223/v1/chat/completions'
    print(f"\nTesting API endpoint: {url}")
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    payload = {
        'model': 'deepseek-chat',
        'messages': [{'role': 'user', 'content': 'test'}]
    }
    
    # Disable SSL verification warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("Sending request...")
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        verify=False,
        timeout=10
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
except requests.exceptions.RequestException as e:
    print(f"\nRequest error occurred: {str(e)}")
    traceback.print_exc()
except Exception as e:
    print(f"\nUnexpected error occurred: {str(e)}")
    traceback.print_exc()

print("\nTest complete")