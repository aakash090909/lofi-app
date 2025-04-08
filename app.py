from flask import Flask, request, send_file, render_template, redirect, url_for
from pydub import AudioSegment
from pydub.effects import low_pass_filter
import os
from uuid import uuid4
import threading

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'ogg', 'flac', 'aac', 'm4a'}
MAX_DURATION_MINUTES = 30  # 30 minutes

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def lofi_process(input_path, output_path):
    try:
        audio = AudioSegment.from_file(input_path)
        duration_minutes = len(audio) / 1000 / 60
        if duration_minutes > MAX_DURATION_MINUTES:
            print(f"[!] Skipped: Duration too long ({duration_minutes:.2f} min)")
            return
        slowed = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * 0.85)
        }).set_frame_rate(audio.frame_rate)
        lofi = low_pass_filter(slowed, cutoff=1500)
        lofi.export(output_path, format="mp3")
        print(f"[✓] Processed: {output_path}")
    except Exception as e:
        print(f"[✖] Processing error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_to_lofi():
    if 'audio' not in request.files:
        return 'No audio file provided', 400

    file = request.files['audio']
    if not allowed_file(file.filename):
        return 'Unsupported file format', 400

    filename = str(uuid4()) + os.path.splitext(file.filename)[1]
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"lofi_{filename}")

    file.save(input_path)

    # Process in a background thread
    threading.Thread(target=lofi_process, args=(input_path, output_path)).start()

    return redirect(url_for('check_status', filename=f"lofi_{filename}"))

@app.route('/status/<filename>')
def check_status(filename):
    output_path = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True)
    return render_template('processing.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
