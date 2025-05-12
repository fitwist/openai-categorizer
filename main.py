from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE = 'https://api.openai.com/v2'


@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Hello, world!'})


@app.route('/create_thread', methods=['POST'])
def create_thread():
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v1'
        }
        
        response = requests.post(
            f'{OPENAI_API_BASE}/threads',
            headers=headers
        )
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': 'Failed to create thread'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/categorize', methods=['POST'])
def categorize():
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        
        if not thread_id:
            return jsonify({'error': 'thread_id is required'}), 400
            
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v1'
        }
        
        response = requests.post(
            f'{OPENAI_API_BASE}/threads/{thread_id}/messages',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': 'Failed to get assistant response'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 