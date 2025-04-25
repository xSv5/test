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

    with open(file_path, 'r') as f:
        print(f.read())

    return jsonify({'status': 'added'}), 200



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

