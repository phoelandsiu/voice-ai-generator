import requests
from dotenv import load_dotenv
import os
import json
import datetime

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PORT = 8000
DIRECTORY = "/Users/phoelandsiu/audio-project"

# Change working directory to serve files from there
import os
os.chdir(DIRECTORY)

print(f"Serving {DIRECTORY} at http://localhost:{PORT}")
ThreadingHTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler).serve_forever()

load_dotenv()

API_KEY = os.getenv('API_KEY')
CACHE_FILE = 'voice_models_cache.json'

def load_cache():
    """Load cached model IDs"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save model ID to cache"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def get_or_create_model(voice_file):

    cache = load_cache()
    cache_key = os.path.basename(voice_file)

    # Check for existing model
    if cache_key in cache:
        model_id = cache[cache_key]['model_id']
        print(f"Using cached model: {model_id}")
        return model_id

    # Create new model
    print(f"Creating new model for {voice_file}...")
    model_id = generate_model(voice_file)

    # Save new model to cache
    cache[cache_key] = {
        'model_id': model_id,
        'file_path': voice_file,
        'created_at': datetime.now().isoformat()
    }
    save_cache(cache)
    print(f"Model created and cached: {model_id}")

    return model_id

def generate_model(voice_file):

    url = "https://api.fish.audio/model"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "visibility": "unlist",
        "type": "tts",
        "title": "streamer-audio",
        "description": "VoiceModel",
        "train_mode": "fast",
        "tags": "voice",
        "enhance_audio_quality": "false"
    }

    files = {
        "voices": open(voice_file, "rb")
    }

    # Try to return model id
    try:
        with open(voice_file, "rb") as f:
            files = {"voices": f}
            response = requests.post(url, headers=headers, data=data, files=files)
            response.raise_for_status()
            
        result = response.json()
        model_id = result['_id']
        print(f"Model ID: {model_id}")
        
        return model_id
        
    except requests.exceptions.RequestException as e:
        print(f"Error creating model: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        raise

def generate_speech(model_id, text, output_file):

    url = "https://api.fish.audio/v1/tts"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "text": f"{text}", 
        "reference_id": f"{model_id}"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        # Save audio data
        with open(output_file, "wb") as f:
            f.write(response.content)
            print(f"Speech generated: {output_file}")
            return output_file
            
    # Otherwise throw error and show details
    except requests.exceptions.RequestException as e:
        print(f"Error generating speech: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {e.response.text[:500]}")
        return None


def main():
    # Define variables
    voice_file = "/Users/phoelandsiu/Downloads/Momo_Audio.mp3"
    model_id = generate_model(voice_file)
    output_file = f"speech_{model_id[:8]}.mp3"

    # Generate audio file
    result = generate_speech(
        model_id = model_id, 
        text = "Hello! This is my first stream!",
        output_file = output_file
    )
    
    if result: 
        print(f"Success! Play with afplay {result}")
    else:
        print("Failed to generate speech")

if __name__ == '__main__':
    main()