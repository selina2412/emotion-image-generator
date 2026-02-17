from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import base64
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

app = Flask(__name__, static_folder='static')

# Configure from environment
FAL_API_KEY = os.environ.get('FAL_API_KEY')
# Use fal.run synchronous endpoints by default; model id should be like 'fal-ai/flux/dev'
FAL_MODEL_ID = os.environ.get('FAL_MODEL_ID', 'fal-ai/flux/dev')
FAL_API_ENDPOINT = os.environ.get('FAL_API_ENDPOINT', f'https://fal.run/{FAL_MODEL_ID}')


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/generate', methods=['POST'])
def generate():
    data = request.json or {}
    emotion = data.get('emotion', 'neutral')
    style = data.get('style', 'minimal')

    # If no API key is configured, return an inline SVG placeholder so frontend can be tested
    if not FAL_API_KEY:
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="768"><rect width="100%" height="100%" fill="#1e1e2f"/><text x="50%" y="50%" fill="#ffd166" font-size="36" text-anchor="middle" dominant-baseline="central">Placeholder: {emotion} {style}</text></svg>'''
        b64 = base64.b64encode(svg.encode()).decode()
        data_url = f'data:image/svg+xml;base64,{b64}'
        return jsonify({'image_url': data_url})

    prompt = f"A {emotion} themed {style} digital artwork, cinematic lighting, high detail"

    # Prepare payload according to fal.ai synchronous API
    payload = {
        'prompt': prompt
    }

    headers = {
        'Authorization': f'Key {FAL_API_KEY}',
        'Content-Type': 'application/json'
    }

    resp = requests.post(FAL_API_ENDPOINT, json=payload, headers=headers, timeout=120)

    if resp.status_code != 200:
        # If the queue/sync endpoint returned a 202 for queueing, surface that
        return jsonify({'error': 'API request failed', 'details': resp.text}), 502

    # Attempt to parse JSON response from fal
    try:
        result = resp.json()
    except Exception:
        result = {}

    # Handle common fal synchronous response shape: { images: [ { url, width, height } ], ... }
    image_url = None
    if isinstance(result, dict) and 'images' in result and isinstance(result['images'], list) and len(result['images']) > 0:
        first = result['images'][0]
        image_url = first.get('url')

    # If the API returned a base64 field
    if not image_url and isinstance(result, dict) and 'image_base64' in result:
        b64 = result['image_base64']
        img_data = base64.b64decode(b64)
        filename = f'static/generated_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}_{uuid.uuid4().hex[:8]}.jpg'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(img_data)
        image_url = '/' + filename.replace('\\', '/')

    # If still not found, maybe the endpoint returned a direct URL in `response` or `image_url`
    if not image_url:
        if isinstance(result, dict) and 'image_url' in result:
            image_url = result['image_url']
        elif isinstance(result, dict) and 'response' in result and isinstance(result['response'], dict):
            # some queue/response shapes wrap the final result
            resp_body = result['response']
            if 'images' in resp_body and isinstance(resp_body['images'], list) and len(resp_body['images']) > 0:
                image_url = resp_body['images'][0].get('url')
            elif 'image_url' in resp_body:
                image_url = resp_body['image_url']

    # As a final fallback, if the response contained binary image bytes, save them
    if not image_url:
        try:
            # If response had content-type image/*, save the bytes
            content_type = resp.headers.get('Content-Type', '')
            if content_type.startswith('image/') or resp.content:
                img_data = resp.content
                filename = f'static/generated_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}_{uuid.uuid4().hex[:8]}.jpg'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'wb') as f:
                    f.write(img_data)
                image_url = '/' + filename.replace('\\', '/')
        except Exception:
            pass

    if not image_url:
        return jsonify({'error': 'No image returned from API', 'details': result}), 502

    return jsonify({'image_url': image_url})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=True)
