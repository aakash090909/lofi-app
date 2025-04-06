from flask import Flask, request, send_file, render_template
from pydub import AudioSegment
from pydub.effects import low_pass_filter
import os
from uuid import uuid4

app = Flask(__name__, template_folder='templates')

# Set max file size to 5MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_to_lofi():
    if 'audio' not in request.files:
        return 'No audio file provided', 400

    file = request.files['audio']
    if file.filename == '':
        return 'No selected file', 400

    filename = str(uuid4()) + os.path.splitext(file.filename)[1]
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"lofi_{filename}.mp3")

    try:
        file.save(input_path)

        # Convert audio
        audio = AudioSegment.from_file(input_path)

# Convert to mono for compatibility
audio = audio.set_channels(1)

# Slow down (lofi effect)
slowed = audio._spawn(audio.raw_data, overrides={
    "frame_rate": int(audio.frame_rate * 0.85)
}).set_frame_rate(audio.frame_rate)

# Apply filter
lofi = low_pass_filter(slowed, cutoff=1500)

        # Export with good quality
        lofi.export(output_path, format="mp3", bitrate="128k")

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Error during conversion: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
