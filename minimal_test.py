import requests
import os
import json
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API configuration
API_KEY = "sk-467710c038f1445e8bc30c4245d7ad92"
API_URL = "http://34.107.189.223/v1/chat/completions"

# Request configuration
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

payload = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "test"}],
    "max_tokens": 5
}

print("Starting minimal test...")
print(f"Using endpoint: {API_URL}")

try:
    # Create session
    session = requests.Session()
    session.verify = False
    
    # Clear any proxy settings
    session.proxies.clear()
    
    # Make request
    print("\nSending request...")
    response = session.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=10
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
except requests.exceptions.RequestException as e:
    print(f"\nRequest error: {str(e)}")
except Exception as e:
    print(f"\nUnexpected error: {str(e)}")

print("\nTest complete")