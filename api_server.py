from flask import Flask, request, send_file, jsonify
from dotenv import load_dotenv
import requests
import os
import tempfile
import json
from datetime import datetime
from pathlib import Path

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv('API_KEY')
CACHE_FILE = 'voice_models_cache.json'

SERVE_DIR = Path.cwd()
SERVE_DIR.mkdir(parents=True, exist_ok=True)

def load_cache():
    """Load cached model IDs"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save model IDs to cache"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

# ============================================
# Endpoint 1: Generate Model
# ============================================
@app.route('/create-model', methods=['POST'])
def create_model():
    """
    POST /create-model
    Form-data:
        - voices: audio file (required)
        - title: model title (optional, default: "streamer-audio")
        - description: model description (optional, default: "VoiceModel")
        - visibility: public/unlist/private (optional, default: "unlist")
        - train_mode: fast/slow (optional, default: "fast")
        - tags: comma-separated tags (optional, default: "voice")
    
    Returns: JSON with model_id
    """
    try:
        # Check if voice file is provided
        if 'voices' not in request.files:
            return jsonify({'error': 'No voice file provided'}), 400
        
        voice_file = request.files['voices']
        
        # Get optional parameters from form
        title = request.form.get('title', 'streamer-audio')
        description = request.form.get('description', 'VoiceModel')
        visibility = request.form.get('visibility', 'unlist')
        train_mode = request.form.get('train_mode', 'fast')
        tags = request.form.get('tags', 'voice')
        enhance_audio = request.form.get('enhance_audio_quality', 'false')
        
        # Prepare request to Fish Audio API
        url = "https://api.fish.audio/model"
        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }
        
        data = {
            "visibility": visibility,
            "type": "tts",
            "title": title,
            "description": description,
            "train_mode": train_mode,
            "tags": tags,
            "enhance_audio_quality": enhance_audio
        }
        
        files = {
            "voices": (voice_file.filename, voice_file.stream, voice_file.content_type)
        }
        
        # Make request to Fish Audio
        response = requests.post(url, headers=headers, data=data, files=files)
        response.raise_for_status()
        
        result = response.json()
        model_id = result['_id']
        
        # Cache the model
        cache = load_cache()
        cache_key = voice_file.filename
        cache[cache_key] = {
            'model_id': model_id,
            'title': title,
            'created_at': datetime.now().isoformat(),
            'state': result.get('state')
        }
        save_cache(cache)
        
        return jsonify({
            'success': True,
            'model_id': model_id,
            'state': result.get('state'),
            'title': title,
            'message': 'Model created successfully'
        }), 201
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_msg = e.response.text
        return jsonify({'error': error_msg}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# Endpoint 2: Generate Audio
# ============================================
@app.route('/generate-speech', methods=['POST'])
def generate_speech():
    """
    POST /generate-speech
    JSON Body:
        {
            "text": "Text to speak",
            "reference_id": "model_id_here"
        }
    
    Returns: MP3 audio file
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        text = data.get('text')
        reference_id = data.get('reference_id')
        
        if not text or not reference_id:
            return jsonify({'error': 'Missing text or reference_id'}), 400
        
        # Prepare request to Fish Audio API
        url = "https://api.fish.audio/v1/tts"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "reference_id": reference_id
        }
        
        # Make request to Fish Audio
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Check if we got audio data
        if len(response.content) < 1000:
            return jsonify({
                'error': 'Invalid response from TTS API',
                'response': response.text
            }), 500
    
        current_datetime = datetime.now()
        datetime_string = current_datetime.strftime("%Y%m%d%H%M%S")
        filename = f"{reference_id}_{datetime_string}.mp3"

        path = SERVE_DIR / filename
        if not path.exists(): 
            path.write_bytes(response.content)

        audio_url = f"http://localhost:8000/{filename}" 
        return jsonify({
            "filename": filename,
            "mime": "audio/mpeg",
            "size_bytes": path.stat().st_size,
            "audio_url": audio_url
        }), 201
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_msg = e.response.text
        return jsonify({'error': error_msg}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# Combined Endpoint: Create Model & Generate Speech
# ============================================
@app.route('/create-and-speak', methods=['POST'])
def create_and_speak():
    """
    POST /create-and-speak
    Form-data:
        - voices: audio file (required)
        - text: text to speak (required)
        - title: model title (optional)
    
    Returns: MP3 audio file
    """
    try:
        if 'voices' not in request.files:
            return jsonify({'error': 'No voice file provided'}), 400
        
        text = request.form.get('text')
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        voice_file = request.files['voices']
        title = request.form.get('title', 'streamer-audio')
        
        # Step 1: Create model
        url = "https://api.fish.audio/model"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        
        data = {
            "visibility": "unlist",
            "type": "tts",
            "title": title,
            "description": "VoiceModel",
            "train_mode": "fast",
            "tags": "voice",
            "enhance_audio_quality": "false"
        }
        
        files = {
            "voices": (voice_file.filename, voice_file.stream, voice_file.content_type)
        }
        
        model_response = requests.post(url, headers=headers, data=data, files=files)
        model_response.raise_for_status()
        model_id = model_response.json()['_id']
        
        # Step 2: Wait for training (fast mode ~30 seconds)
        import time
        time.sleep(35)
        
        # Step 3: Generate speech
        tts_url = "https://api.fish.audio/v1/tts"
        tts_headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        tts_payload = {
            "text": text,
            "reference_id": model_id
        }
        
        tts_response = requests.post(tts_url, headers=tts_headers, json=tts_payload)
        tts_response.raise_for_status()
        
        # Save and return audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.write(tts_response.content)
        temp_file.close()
        
        return send_file(
            temp_file.name,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=f'{model_id}.mp3'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ============================================
# Helper Endpoints
# ============================================
@app.route('/models', methods=['GET'])
def list_models():
    """
    GET /models
    Returns: List of cached models
    """
    cache = load_cache()
    return jsonify(cache)

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'api_key_set': bool(API_KEY)})

if __name__ == '__main__':
    if not API_KEY:
        print("Warning: API_KEY not found in .env file")
    else:
        print(f"API Key loaded")
    
    print("\nAvailable endpoints:")
    print("  POST /create-model        - Upload voice and create model")
    print("  POST /generate-speech     - Generate speech from model")
    print("  POST /create-and-speak    - Create model and generate speech")
    print("  GET  /models              - List cached models")
    print("  GET  /health              - Health check")
    
    app.run(host='0.0.0.0', port=5000, debug=True)