from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from datetime import datetime

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

file_path = 'keys.info'
key = b'65erfEfuyTHhGfJF'
iv = b'75erv8FuyjgbUY4f'

@app.route('/')
def index():
    return 'OK'

def decrypt_and_compare(encrypted_key):
    try:
        encrypted_date = base64.b64decode(encrypted_key)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_date) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        decrypted_date = unpadded_data.decode()
        current_date = datetime.now().strftime('%Y-%m-%d')
        print("Decrypted Date:", decrypted_date)
        print("Current Date:", current_date)
        return decrypted_date == current_date
    except Exception as e:
        print("Error during decryption:", str(e))
        return False

@app.route('/new', methods=['POST'])
@limiter.limit("5 per minute")
def new():
    data = request.get_json()
    if not data or 'key' not in data or 'license_key' not in data:
        return jsonify({'error': 'Invalid JSON or missing key/license_key'}), 400

    keyv = data['key']
    license_key = data['license_key']
    print(f"Received key: {keyv}")

    if decrypt_and_compare(keyv):
        existing = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    existing = json.load(f)
                except:
                    existing = []

        existing.append(license_key)
        with open(file_path, 'w') as f:
            json.dump(existing, f)

        return jsonify({'status': 'Successfully added license'}), 200
    else:
        return jsonify({'status': 'Failed to authenticate'}), 401

@app.route('/verify', methods=['POST'])
@limiter.limit("5 per minute")
def verify():
    data = request.get_json()
    if not data or 'license_key' not in data:
        return jsonify({'error': 'Invalid JSON or missing license_key'}), 400

    license_key = data['license_key']
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                existing = json.load(f)
            except:
                existing = []

        if license_key in existing:
            return jsonify({'status': 'License key is valid'}), 200
        else:
            return jsonify({'status': 'License key is not valid'}), 404
    else:
        return jsonify({'error': 'License file not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
