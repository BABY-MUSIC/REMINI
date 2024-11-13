from flask import Flask, request, jsonify, send_file
import subprocess
import os
from werkzeug.utils import secure_filename
import uuid

# Flask app initialization
app = Flask(__name__)

# Set the maximum file size for uploading (e.g., 10MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

# Path for your Waifu2x and input/output images
WAIFU2X_PATH = '/path/to/waifu2x'  # Change this to your actual Waifu2x directory
OUTPUT_DIR = './enhanced_images'  # Directory to save enhanced images

# File upload settings
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    """Check if the uploaded file is an allowed image type."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/enhance', methods=['POST'])
def enhance_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Generate a unique filename for the input and output images
        unique_filename = str(uuid.uuid4())
        input_path = os.path.join(OUTPUT_DIR, f"{unique_filename}_input.jpg")
        output_path = os.path.join(OUTPUT_DIR, f"{unique_filename}_output.jpg")

        # Save the uploaded file to the server
        file.save(input_path)

        # Run Waifu2x command to enhance the image (2x scale)
        command = f"th {WAIFU2X_PATH}/waifu2x.lua -i {input_path} -o {output_path} -s 2"
        subprocess.run(command, shell=True)

        # Check if output image exists, if not, return error
        if os.path.exists(output_path):
            # Return the enhanced image file to the user
            return send_file(output_path, mimetype='image/jpeg')

        return jsonify({"error": "Image enhancement failed"}), 500

    return jsonify({"error": "Invalid file type"}), 400

if __name__ == '__main__':
    # Ensure the output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Run the Flask server
    app.run(debug=True, host='0.0.0.0', port=5000)
