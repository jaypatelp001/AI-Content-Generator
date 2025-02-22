import os
import base64
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import logging
from ai_utils import generate_hashtags, generate_caption, generate_script

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-hashtags', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400

        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a PNG or JPEG image.'}), 400

        # Convert image to base64
        image_data = base64.b64encode(file.read()).decode('utf-8')
        hashtags = generate_hashtags(image_data)

        return jsonify({'hashtags': hashtags})
    except Exception as e:
        error_message = str(e)
        if 'rate limit' in error_message.lower():
            status_code = 429
        else:
            status_code = 500
        logging.error(f"Error processing image: {error_message}")
        return jsonify({'error': error_message}), status_code

@app.route('/generate-caption', methods=['POST'])
def create_caption():
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({'error': 'Please provide a topic for the caption'}), 400

        caption = generate_caption(topic)
        return jsonify({'caption': caption})
    except Exception as e:
        error_message = str(e)
        if 'rate limit' in error_message.lower():
            status_code = 429
        else:
            status_code = 500
        logging.error(f"Error generating caption: {error_message}")
        return jsonify({'error': error_message}), status_code

@app.route('/generate-script', methods=['POST'])
def create_script():
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({'error': 'Please provide a topic for the script'}), 400

        script = generate_script(topic)
        return jsonify({'script': script})
    except Exception as e:
        error_message = str(e)
        if 'rate limit' in error_message.lower():
            status_code = 429
        else:
            status_code = 500
        logging.error(f"Error generating script: {error_message}")
        return jsonify({'error': error_message}), status_code