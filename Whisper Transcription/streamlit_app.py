import streamlit as st
import requests

# Título de la aplicación
st.title("Transcripción y Resumen de Audio")

# Subtítulo
st.markdown("Sube un archivo de audio, obtén la transcripción y resúmela.")

# Inicializar variables en session_state si no existen
if "transcription" not in st.session_state:
    st.session_state.transcription = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

# Widget para subir archivos de audio
audio_file = st.file_uploader("Sube un archivo de audio", type=["wav", "mp3"])

# Botón para transcribir el audio
if st.button("Transcribir Audio"):
    if audio_file is not None:
        with st.spinner("Transcribiendo audio..."):
            files = {"audio": audio_file}
            response = requests.post("http://127.0.0.1:5000/transcribe", files=files)

            if response.status_code == 200:
                st.session_state.transcription = response.json().get("transcription", "")
            else:
                st.error(f"Error al transcribir el audio: {response.json().get('error', 'Error desconocido')}")

# Mostrar la transcripción si existe
if st.session_state.transcription:
    st.text_area("Transcripción", st.session_state.transcription, height=200)

# Botón para resumir el texto transcrito
if st.session_state.transcription:
    if st.button("Resumir"):
        with st.spinner("Resumiendo texto..."):
            data = {"text": st.session_state.transcription}
            response = requests.post("http://127.0.0.1:5000/summarize", json=data)

            if response.status_code == 200:
                st.session_state.summary = response.json().get("summary", "")
            else:
                st.error(f"Error al resumir el texto: {response.json().get('error', 'Error desconocido')}")

# Mostrar el resumen si existe
if st.session_state.summary:
    st.text_area("Resumen", st.session_state.summary, height=100)
