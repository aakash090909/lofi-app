from flask import Flask, render_template, request, send_file
from pydub import AudioSegment
from pydub.effects import speedup, low_pass_filter
import os

app = Flask(__name__)

def convert_to_lofi(audio_path):
    try:
        song = AudioSegment.from_file(audio_path)
        slowed = speedup(song, playback_speed=0.85)
        lofi = low_pass_filter(slowed, cutoff=1500)
        return lofi
    except Exception as e:
        print("Error during conversion:", e)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['file']
    filename = "original.wav"
    file.save(filename)

    output = convert_to_lofi(filename)
    if output:
        output_path = "lofi.wav"
        output.export(output_path, format="wav")
        return send_file(output_path, as_attachment=True)
    return "Conversion failed", 500
