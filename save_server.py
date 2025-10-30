from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json, datetime

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)


@app.route('/save_placement', methods=['POST'])
def save_placement():
    try:
        payload = request.get_json(force=True)
        if payload is None:
            return jsonify({'error': 'No JSON payload received'}), 400
        participant = payload.get('participant_number', 'unknown')
        participant = str(participant)
        timestamp = datetime.datetime.utcnow().isoformat().replace(':', '-').replace('.', '-')
        filename = f"P{participant}_{timestamp}.json"
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return jsonify({'status': 'saved', 'filename': filename}), 200
    except Exception as e:
        app.logger.exception('Error saving placement')
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
