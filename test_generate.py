import requests
import time
import sys

URL = 'http://127.0.0.1:7860/generate'

payload = {'emotion': 'hope', 'style': 'minimal'}

# wait for server to become available
for i in range(15):
    try:
        r = requests.post(URL, json=payload, timeout=10)
        print('Status:', r.status_code)
        try:
            print('JSON:', r.json())
        except Exception:
            print('Text:', r.text[:1000])
        sys.exit(0)
    except requests.exceptions.RequestException as e:
        print('Attempt', i+1, 'failed:', e)
        time.sleep(1)

print('Server did not respond in time')
sys.exit(2)
