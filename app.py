import streamlit as st
import os
from pydub import AudioSegment
from pydub.effects import speedup

# ===== CONFIGURACIÓN DE LA PÁGINA =====
st.set_page_config(
    page_title="AKI 😺 Audio Converter",
    page_icon="😺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ===== ESTILOS CSS (Diseño oscuro estilo Nomen) =====
st.markdown("""
    <style>
    /* Fondo oscuro general */
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    /* Título principal */
    h1 {
        color: #ffffff !important;
        font-family: 'Arial Black', sans-serif;
        text-align: center;
    }
    
    /* Subtítulos y textos */
    p, label, .stMarkdown {
        color: #b0b0b0 !important;
    }
    
    /* Caja de subida de archivos */
    .stFileUploader {
        background-color: #1a1a1a;
        border: 2px dashed #333;
        border-radius: 15px;
        padding: 20px;
    }
    
    /* Botones */
    .stButton > button {
        background-color: #8b5cf6;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #7c3aed;
    }
    
    /* Slider */
    .stSlider > div > div > div > div {
        background-color: #8b5cf6;
    }
    
    /* Caja de métricas */
    .stMetric {
        background-color: #1a1a1a;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #333;
    }
    
    /* Reproductor de audio */
    audio {
        width: 100%;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ===== LOGO Y TÍTULO =====
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.png", width=200)
    except:
        st.markdown("# 😺")

st.markdown("<h1>AKI 😺 Audio Converter</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Sube tu canción, escúchala, ajusta el pitch y descarga el archivo listo para Roblox.</p>", unsafe_allow_html=True)

st.markdown("---")

# ===== CONFIGURACIÓN =====
MAX_DURATION_SEC = 7 * 60
DEFAULT_PITCH = 0.794

def cambiar_pitch(audio, factor):
    nuevos_frames = int(audio.frame_rate * factor)
    if nuevos_frames < 1000:
        raise ValueError("El factor de pitch es demasiado bajo.")
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": nuevos_frames
    }).set_frame_rate(audio.frame_rate)

def ajustar_duracion(audio, max_seg=MAX_DURATION_SEC):
    duracion = len(audio) / 1000.0
    if duracion <= max_seg:
        return audio, 1.0
    factor = duracion / max_seg
    return speedup(audio, playback_speed=factor, chunk_size=150), factor

# ===== SUBIR ARCHIVO =====
archivo_subido = st.file_uploader("🎵 Arrastra tu canción aquí", type=["mp3", "wav", "ogg", "flac"])

if archivo_subido is not None:
    st.markdown("### 🎚️ Ajusta el Pitch")
    pitch_usuario = st.slider("Pitch (Shift)", 0.5, 1.5, DEFAULT_PITCH, 0.001)
    
    # Reproductor de audio original
    st.markdown("### 🎧 Escucha tu canción original")
    st.audio(archivo_subido, format="audio/mp3")
    
    if st.button("🔄 Convertir ahora"):
        with st.spinner("Procesando audio..."):
            try:
                audio = AudioSegment.from_file(archivo_subido)
                audio_pitch = cambiar_pitch(audio, pitch_usuario)
                audio_final, speed_factor = ajustar_duracion(audio_pitch, MAX_DURATION_SEC)
                effect_speed = round(pitch_usuario * speed_factor, 4)
                output_buffer = audio_final.export(format="mp3", bitrate="192k")
                
                st.success("¡Conversión exitosa! 🎉")
                
                # Reproducir el audio convertido
                st.markdown("### 🔊 Escucha tu canción convertida")
                st.audio(output_buffer, format="audio/mp3")
                
                # Métricas
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(label="EffectSpeed para NekoDJ", value=effect_speed)
                with col_b:
                    st.metric(label="Duración final", value=f"{len(audio_final)/1000:.2f} seg")
                
                # Botón de descarga
                st.download_button(
                    label="📥 Descargar Audio Convertido",
                    data=output_buffer,
                    file_name=f"{os.path.splitext(archivo_subido.name)[0]}_aki.mp3",
                    mime="audio/mpeg"
                )
            except Exception as e:
                st.error(f"Error al procesar: {e}")
