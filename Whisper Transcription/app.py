from flask import Flask, request, jsonify
from transformers import pipeline
import subprocess

app = Flask(__name__)

# Verificar si FFmpeg está instalado
def is_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

# Cargar el modelo Whisper
def load_whisper_model():
    try:
        if not is_ffmpeg_installed():
            raise Exception("FFmpeg no está instalado. Por favor, instálalo y agrega la ruta al PATH.")
        transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-small", return_timestamps=True)
        print("Modelo Whisper cargado correctamente.")
        return transcriber
    except Exception as e:
        print("Error al cargar el modelo Whisper:", str(e))
        return None

# Cargar el modelo de resumen
def load_summarizer():
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        print("Modelo de resumen cargado correctamente.")
        return summarizer
    except Exception as e:
        print("Error al cargar el modelo de resumen:", str(e))
        return None

# Cargar ambos modelos
transcriber = load_whisper_model()
summarizer = load_summarizer()

# Ruta principal
@app.route("/")
def home():
    return """
    <h1>Bienvenido a la API de Transcripción y Resumen</h1>
    <p>Endpoints disponibles:</p>
    <ul>
        <li><strong>/transcribe</strong>: Envía un archivo de audio para transcribirlo (POST).</li>
        <li><strong>/summarize</strong>: Envía un texto para resumirlo (POST).</li>
    </ul>
    """

# Ruta para transcribir audio
@app.route("/transcribe", methods=["POST"])
def transcribe():
    if transcriber is None:
        return jsonify({"error": "El modelo Whisper no está disponible"}), 500

    if "audio" not in request.files:
        return jsonify({"error": "No se proporcionó un archivo de audio"}), 400

    try:
        audio_file = request.files["audio"]
        transcription = transcriber(audio_file.read())
        return jsonify({"transcription": transcription["text"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para resumir texto
@app.route("/summarize", methods=["POST"])
def summarize():
    if summarizer is None:
        return jsonify({"error": "El modelo de resumen no está disponible"}), 500

    if "text" not in request.json:
        return jsonify({"error": "No se proporcionó un texto"}), 400

    try:
        text = request.json["text"]
        summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
        return jsonify({"summary": summary[0]["summary_text"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)