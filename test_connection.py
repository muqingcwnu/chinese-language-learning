from decouple import config
import requests
import json

def test_connection():
    api_key = config('DEEPSEEK_API_KEY')
    url = "https://api.deepseek.ai/v1/chat/completions"
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": "你好"
            }
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Disable SSL verification for Windows
        response = requests.post(url, json=payload, headers=headers, verify=False)
        
        # Write results to a file
        with open('api_test_results.txt', 'w', encoding='utf-8') as f:
            f.write(f"Status Code: {response.status_code}\n")
            f.write(f"Response Headers: {dict(response.headers)}\n")
            f.write(f"Response Body: {response.text}\n")
            
        return response.status_code == 200
        
    except Exception as e:
        with open('api_test_results.txt', 'w', encoding='utf-8') as f:
            f.write(f"Error: {str(e)}\n")
        return False

if __name__ == "__main__":
    test_connection()
