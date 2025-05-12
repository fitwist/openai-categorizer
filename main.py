from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE = 'https://api.openai.com/v1'


@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Hello, world!'})


@app.route('/create_thread', methods=['POST'])
def create_thread():
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }
        
        response = requests.post(
            f'{OPENAI_API_BASE}/threads',
            headers=headers,
            json={}
        )
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': 'Failed to create thread', 'details': response.text}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/categorize/<thread_id>', methods=['POST'])
def categorize(thread_id):
    try:
        data = request.get_json()
        role = data.get('role')
        content = data.get('content')

        if not role or not content:
            return jsonify({'error': 'role and content are required'}), 400

        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }

        payload = {
            "role": role,
            "content": content
        }

        response = requests.post(
            f'{OPENAI_API_BASE}/threads/{thread_id}/messages',
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': 'Failed to get assistant response', 'details': response.text}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 