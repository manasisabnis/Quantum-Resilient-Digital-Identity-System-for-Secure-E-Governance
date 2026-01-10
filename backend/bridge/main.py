from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(BASE_DIR)
from crypto_modules.hashing import SHA3Hash

app = Flask(__name__)
CORS(app)

# MongoDB connection (MONGODB_URI env or default local)
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'user_db')

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
users = db['users']


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'message': 'Invalid or missing JSON'}), 400

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'message': 'username, password and email are required'}), 400

    # simple duplicate check by username or email
    existing = users.find_one({'$or': [{'username': username}, {'email': email}]})
    if existing:
        return jsonify({'message': 'User with that username or email already exists'}), 409

    doc = {
        'username': username,
        'password': password,  # demo only; DO NOT store plaintext in production
        'email': email,
    }

    result = users.insert_one(doc)

# ---- BRIDGE ADDITION START ----
# Create deterministic data to hash (demo-safe)
    data_to_hash = f"{username}:{email}".encode()

# SHA3-256 → 64 hex chars (NO 0x)
    digest = SHA3Hash.hexdigest(data_to_hash)
# ---- BRIDGE ADDITION END ----
    print("DEBUG HASH:", digest, len(digest))

    return jsonify({
    "id": str(result.inserted_id),
    "hash": digest
     }), 201



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)