import threading
from flask import Flask, request, jsonify, send_file
import subprocess
import os
from werkzeug.utils import secure_filename
import uuid
import telegram
from io import BytesIO

# Flask app initialization
app = Flask(__name__)

# Telegram Bot Token and API setup
TOKEN = '7638229482:AAEU9eVchpJco0FhOR1f3Xn6t1oQjwt9a2s'  # Yahan apna Telegram bot token daalein
bot = telegram.Bot(token=TOKEN)

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

# Telegram Bot Handler
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    chat_id = update['message']['chat']['id']
    
    if 'photo' in update['message']:
        file_id = update['message']['photo'][-1]['file_id']  # Get the highest resolution photo
        file = bot.get_file(file_id)
        file.download('user_image.jpg')  # Download the image from Telegram
        
        # Enhance the image using Waifu2x
        enhanced_image = enhance_image('user_image.jpg')
        
        # Send the enhanced image back to the user
        with open(enhanced_image, 'rb') as f:
            bot.send_photo(chat_id=chat_id, photo=f)
        
        # Clean up the temporary files
        os.remove('user_image.jpg')
        os.remove(enhanced_image)
        
    return jsonify({"status": "success"}), 200

def enhance_image(input_path):
    """Enhance the image using Waifu2x"""
    # Generate a unique filename for the output
    unique_filename = str(uuid.uuid4())
    output_path = os.path.join(OUTPUT_DIR, f"{unique_filename}_output.jpg")

    # Run Waifu2x command to enhance the image (2x scale)
    command = f"th {WAIFU2X_PATH}/waifu2x.lua -i {input_path} -o {output_path} -s 2"
    subprocess.run(command, shell=True)

    return output_path

def run_webhook():
    """Run webhook setup in a separate thread"""
    webhook_url = 'https://your-server-ip-or-domain/webhook'  # Replace with your actual server URL
    bot.set_webhook(url=webhook_url)

if __name__ == '__main__':
    # Ensure the output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Set webhook for Telegram bot in a background thread
    thread = threading.Thread(target=run_webhook)
    thread.start()

    # Run the Flask server
    app.run(debug=True, host='0.0.0.0', port=5000)
