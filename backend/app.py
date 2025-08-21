from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import face_recognition

# Paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
# The static folder is now the 'build' folder from React
app = Flask(__name__, static_folder=os.path.join(backend_dir, 'build'), static_url_path='/')
CORS(app, resources={r"/*": {"origins": "*"}}) # Allow all origins for simplicity in deployment

# DB and temp
DB_PATH = os.path.join(backend_dir, 'voters.db')
TEMP_FOLDER = os.path.join(backend_dir, 'temp')
os.makedirs(TEMP_FOLDER, exist_ok=True)

# DB connection
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Get voter
def get_voter_details(voter_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT photo_path, has_voted FROM voters WHERE voter_id = ?", (voter_id,))
        voter = cur.fetchone()
        conn.close()
        return voter
    except sqlite3.Error as e:
        print(f"DB Error: {e}")
        return None

# Allow headers/methods
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# API Routes
@app.route('/check_id', methods=['POST'])
def check_id_route():
    data = request.get_json()
    voter_id = data.get('voter_id', '').strip()
    print(f"🔎 Checking ID: {voter_id}")
    if not voter_id:
        return jsonify({'valid': False, 'message': 'Voter ID cannot be empty.'}), 400
    voter = get_voter_details(voter_id)
    if voter:
        if voter['has_voted']:
            return jsonify({'valid': False, 'message': f'Voter ID {voter_id} has already voted.'})
        return jsonify({'valid': True, 'message': f'Voter ID {voter_id} is valid.'})
    return jsonify({'valid': False, 'message': f'Voter ID {voter_id} not found.'})

@app.route('/verify_face', methods=['POST'])
def verify_face_route():
    print("✅ /verify_face route hit")
    voter_id = request.form.get('voter_id')
    photo_file = request.files.get('photo')
    print(f"📩 Received voter_id={voter_id}, photo_file={photo_file}")

    if not voter_id or not photo_file:
        return jsonify({'match': False, 'message': 'Missing voter ID or photo.'}), 400

    captured_path = os.path.join(TEMP_FOLDER, f'{voter_id}_capture.jpg')
    try:
        photo_file.save(captured_path)
    except Exception as e:
        print(f"❌ Error saving photo: {e}")
        return jsonify({'match': False, 'message': 'Could not save photo.'}), 500

    voter = get_voter_details(voter_id)
    if not voter:
        os.remove(captured_path)
        return jsonify({'match': False, 'message': 'Voter ID not found.'}), 404

    stored_path = os.path.join(backend_dir, voter['photo_path'])
    if not os.path.exists(stored_path):
        os.remove(captured_path)
        return jsonify({'match': False, 'message': 'Stored photo not found.'}), 500

    is_match = False
    message = 'Face verification failed.'

    try:
        known_img = face_recognition.load_image_file(stored_path)
        unknown_img = face_recognition.load_image_file(captured_path)

        known_enc = face_recognition.face_encodings(known_img)
        unknown_enc = face_recognition.face_encodings(unknown_img)

        if not known_enc:
            message = 'No face in registered photo.'
        elif not unknown_enc:
            message = 'No face detected in captured photo.'
        else:
            result = face_recognition.compare_faces([known_enc[0]], unknown_enc[0], tolerance=0.6)
            is_match = result[0]
            if is_match:
                message = 'Face matched. Vote recorded.'
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("UPDATE voters SET has_voted = 1 WHERE voter_id = ?", (voter_id,))
                conn.commit()
                conn.close()
            else:
                message = 'Face did not match.'
    except Exception as e:
        print(f"❌ Face match error: {e}")
        message = 'Face verification error.'

    finally:
        if os.path.exists(captured_path):
            os.remove(captured_path)

    return jsonify({'match': bool(is_match), 'message': message})

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(use_reloader=True, port=5000, threaded=True)