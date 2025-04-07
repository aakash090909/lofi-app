from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "App is running!"

@app.route("/health")
def health():
    return "Healthy", 200