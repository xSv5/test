from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
file_path = 'keys.info'

@app.route('/')
def index():
    return 'OK'

@app.route('/new', methods=['POST'])
def new():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    existing = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                existing = json.load(f)
            except:
                existing = []

    existing.append(data)

    with open(file_path, 'w') as f:
        json.dump(existing, f)

    return jsonify({'status': 'added'}), 200

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    if not data or 'key' not in data:
        return jsonify({'error': 'Invalid JSON or missing key'}), 400

    key_to_verify = data['key']
    existing = []

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                existing = json.load(f)
            except:
                existing = []

    # Check if the key exists in the existing list
    for entry in existing:
        if 'key' in entry and entry['key'] == key_to_verify:
            return jsonify({'status': 'key found'}), 200

    return jsonify({'status': 'key not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
