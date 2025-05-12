from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import time

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


@app.route('/send_query/<thread_id>', methods=['POST'])
def send_query(thread_id):
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


@app.route('/get_category/<thread_id>/<run_id>', methods=['GET'])
def get_category(thread_id, run_id):
    try:
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }

        # Ждём завершения run
        status = None
        for _ in range(60):  # до 60 секунд ожидания
            run_resp = requests.get(
                f'{OPENAI_API_BASE}/threads/{thread_id}/runs/{run_id}',
                headers=headers
            )
            if run_resp.status_code != 200:
                return jsonify({'error': 'Failed to get run status', 'details': run_resp.text}), run_resp.status_code
            run_data = run_resp.json()
            status = run_data.get('status')
            if status == 'completed':
                break
            elif status in ('failed', 'cancelled', 'expired'):
                return jsonify({'error': f'Run status: {status}', 'details': run_data}), 400
            time.sleep(1)
        else:
            return jsonify({'error': 'Timeout waiting for run completion'}), 504

        # Получаем последнее сообщение ассистента
        messages_resp = requests.get(
            f'{OPENAI_API_BASE}/threads/{thread_id}/messages',
            headers=headers
        )
        if messages_resp.status_code != 200:
            return jsonify({'error': 'Failed to get messages', 'details': messages_resp.text}), messages_resp.status_code
        messages = messages_resp.json().get('data', [])
        assistant_message = next((m for m in reversed(messages) if m.get('role') == 'assistant'), None)
        if not assistant_message:
            return jsonify({'error': 'No assistant message found'}), 404
        return jsonify({'assistant_message': assistant_message}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/start_run/<thread_id>', methods=['POST'])
def start_run(thread_id):
    try:
        data = request.get_json()
        assistant_id = data.get('assistant_id')
        if not assistant_id:
            return jsonify({'error': 'assistant_id is required'}), 400

        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v2'
        }

        payload = {
            "assistant_id": assistant_id
        }

        response = requests.post(
            f'{OPENAI_API_BASE}/threads/{thread_id}/runs',
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': 'Failed to start run', 'details': response.text}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 