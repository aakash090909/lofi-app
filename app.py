from flask import Flask, request, send_file, render_template
from pydub import AudioSegment
from pydub.effects import low_pass_filter
import os
from uuid import uuid4

app = Flask(__name__, template_folder='templates')

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Max file size 5MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_to_lofi():
    if 'audio' not in request.files:
        return 'No audio file provided', 400

    file = request.files['audio']
    filename = str(uuid4()) + os.path.splitext(file.filename)[1]
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"lofi_{filename}")

    file.save(input_path)

    try:
        audio = AudioSegment.from_file(input_path)

        # Safe conversion: keep stereo if stereo, mono if mono
        if audio.channels > 2:
            audio = audio.set_channels(2)
        elif audio.channels == 1:
            pass  # already mono
        else:
            audio = audio.set_channels(2)  # fallback to stereo

        # Slow down the audio
        slowed = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * 0.85)
        }).set_frame_rate(audio.frame_rate)

        # Apply low-pass filter
        lofi = low_pass_filter(slowed, cutoff=1500)

        # Export to mp3
        lofi.export(output_path, format="mp3")

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print("Error:", e)
        return "An error occurred while processing the audio.", 500

if __name__ == '__main__':
    app.run(debug=True)
