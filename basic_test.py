print("Test starting...")

import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import requests
    print("\nTesting internet connection...")
    response = requests.get('https://www.google.com')
    print(f"Internet connection works: {response.status_code}")
except Exception as e:
    print(f"Connection error: {e}")

print("\nTest complete")