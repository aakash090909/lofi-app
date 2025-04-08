from flask import Flask, request, send_file, render_template, redirect, url_for
from celery import Celery
from pydub import AudioSegment
from pydub.effects import low_pass_filter
import os
from uuid import uuid4

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Celery config
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'ogg', 'flac', 'aac', 'm4a'}
MAX_DURATION_MINUTES = 30

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@celery.task
def process_lofi(input_path, output_path):
    try:
        audio = AudioSegment.from_file(input_path)
        duration_minutes = len(audio) / 1000 / 60
        if duration_minutes > MAX_DURATION_MINUTES:
            return "Too long"
        slowed = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * 0.85)
        }).set_frame_rate(audio.frame_rate)
        lofi = low_pass_filter(slowed, cutoff=1500)
        lofi.export(output_path, format="mp3")
        return "done"
    except Exception as e:
        return str(e)

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
    output_filename = f"lofi_{filename}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    file.save(input_path)

    task = process_lofi.delay(input_path, output_path)
    return redirect(url_for('check_status', filename=output_filename, task_id=task.id))

@app.route('/status/<task_id>/<filename>')
def check_status(task_id, filename):
    result = process_lofi.AsyncResult(task_id)
    if result.state == 'SUCCESS':
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(output_path):
            return send_file(output_path, as_attachment=True)
        else:
            return "File not found", 404
    elif result.state == 'FAILURE':
        return f"Error: {result.info}", 500
    return render_template('processing.html', filename=filename, task_id=task_id)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
