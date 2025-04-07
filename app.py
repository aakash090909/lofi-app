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

    # Load and apply lofi effect
    audio = AudioSegment.from_file(input_path)
    slowed = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * 0.85)
    }).set_frame_rate(audio.frame_rate)
    lofi = low_pass_filter(slowed, cutoff=1500)
    lofi.export(output_path, format="mp3")

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
