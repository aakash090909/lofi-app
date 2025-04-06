from flask import Flask, render_template, request, send_file
from pydub import AudioSegment
from pydub.effects import speedup, low_pass_filter
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

def convert_to_lofi(audio_path):
    try:
        song = AudioSegment.from_file(audio_path)
        slowed = speedup(song, playback_speed=0.85)
        lofi = low_pass_filter(slowed, cutoff=1500)
        return lofi
    except Exception as e:
        print("Error during conversion:", e)
        return None

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, "original.wav")
    file.save(filepath)

    output = convert_to_lofi(filepath)
    if output:
        output_path = os.path.join(UPLOAD_FOLDER, "lofi.wav")
        output.export(output_path, format="wav")
        return send_file(output_path, as_attachment=True)
    return "Conversion failed", 500

if __name__ == '__main__':
    app.run(debug=True)
