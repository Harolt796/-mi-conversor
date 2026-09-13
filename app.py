import streamlit as st
import streamlit.components.v1 as components
import os
from pydub import AudioSegment
from pydub.effects import speedup
import base64

# ===== CONFIGURACIÓN =====
st.set_page_config(
    page_title="AKI 😺 Audio Converter",
    page_icon="😺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ===== ESTILOS CSS =====
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, #ffffff 0%, #d3d3d3 25%, #4a4a4a 65%, #0a0a0a 100%);
        background-attachment: fixed;
        color: #ffffff;
    }
    h1 {
        color: #ffffff !important;
        font-family: 'Arial Black', sans-serif;
        text-align: center;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
    }
    p, label, .stMarkdown {
        color: #f0f0f0 !important;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.6);
    }
    .stFileUploader {
        background-color: rgba(26, 26, 26, 0.85);
        border: 2px dashed #8b5cf6;
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(5px);
    }
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
    .stSlider > div > div > div > div {
        background-color: #8b5cf6;
    }
    .stMetric {
        background-color: rgba(26, 26, 26, 0.85);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #8b5cf6;
        backdrop-filter: blur(5px);
    }
    audio { width: 100%; border-radius: 10px; }
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
st.markdown("<p style='text-align: center;'>Sube tu canción, escúchala, ajusta la velocidad en vivo y descarga el archivo listo para Roblox.</p>", unsafe_allow_html=True)
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
    # Guardamos el archivo temporalmente para poder leerlo
    temp_path = f"/tmp/{archivo_subido.name}"
    with open(temp_path, "wb") as f:
        f.write(archivo_subido.getbuffer())
    
    # Convertimos el audio a base64 para meterlo dentro del HTML/JS
    audio_bytes = open(temp_path, "rb").read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    
    st.markdown("### 🎧 Reproductor en vivo")
    st.caption("Mueve el slider mientras suena la música para escuchar el cambio en tiempo real. Dale Play primero ▶️")
    
    # ===== REPRODUCTOR HTML/JS CON VELOCIDAD EN VIVO =====
    html_player = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            background: transparent;
            font-family: Arial, sans-serif;
            color: white;
            margin: 0;
            padding: 10px;
        }}
        .player {{
            background: rgba(26, 26, 26, 0.9);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid #8b5cf6;
        }}
        audio {{ width: 100%; margin-bottom: 15px; }}
        .controls {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
        }}
        .controls label {{ color: #b0b0b0; font-size: 14px; white-space: nowrap; }}
        input[type=range] {{
            flex: 1;
            -webkit-appearance: none;
            height: 8px;
            border-radius: 5px;
            background: #333;
            outline: none;
        }}
        input[type=range]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #8b5cf6;
            cursor: pointer;
        }}
        .value {{
            background: #8b5cf6;
            padding: 5px 12px;
            border-radius: 8px;
            font-weight: bold;
            min-width: 70px;
            text-align: center;
        }}
        .info {{
            color: #b0b0b0;
            font-size: 12px;
            margin-top: 10px;
        }}
    </style>
    </head>
    <body>
        <div class="player">
            <audio id="audio" controls src="data:audio/mp3;base64,{audio_b64}"></audio>
            
            <div class="controls">
                <label>🎚️ Velocidad:</label>
                <input type="range" id="speed" min="0.5" max="1.5" step="0.01" value="1.0">
                <span class="value" id="speedValue">1.00x</span>
            </div>
            
            <div class="info">
                💡 Mueve la barra mientras suena para oír el cambio en tiempo real. 
                El valor <b>1.00x</b> es la velocidad original.
            </div>
        </div>
        
        <script>
            const audio = document.getElementById('audio');
            const speed = document.getElementById('speed');
            const speedValue = document.getElementById('speedValue');
            
            // Aplicar velocidad inicial
            audio.playbackRate = parseFloat(speed.value);
            
            // Cambiar velocidad en tiempo real
            speed.addEventListener('input', function() {{
                const rate = parseFloat(this.value);
                audio.playbackRate = rate;
                speedValue.textContent = rate.toFixed(2) + 'x';
            }});
        </script>
    </body>
    </html>
    """
    
    components.html(html_player, height=250)
    
    st.markdown("---")
    st.markdown("### 🎚️ Ajustes para la conversión final")
    st.caption("Aquí eliges el valor exacto que quieres que tenga el archivo final. El valor 0.794 es el estándar de NekoDJ.")
    
    pitch_usuario = st.slider("Pitch (Shift) para exportar", 0.5, 1.5, DEFAULT_PITCH, 0.001)
    
    if st.button("🔄 Convertir y exportar"):
        with st.spinner("Procesando audio completo..."):
            try:
                audio = AudioSegment.from_file(archivo_subido)
                audio_pitch = cambiar_pitch(audio, pitch_usuario)
                audio_final, speed_factor = ajustar_duracion(audio_pitch, MAX_DURATION_SEC)
                effect_speed = round(pitch_usuario * speed_factor, 4)
                output_buffer = audio_final.export(format="mp3", bitrate="192k")
                
                st.success("¡Conversión exitosa! 🎉")
                
                st.markdown("### 🔊 Escucha tu canción convertida")
                st.audio(output_buffer, format="audio/mp3")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(label="EffectSpeed para NekoDJ", value=effect_speed)
                with col_b:
                    st.metric(label="Duración final", value=f"{len(audio_final)/1000:.2f} seg")
                
                st.download_button(
                    label="📥 Descargar Audio Convertido",
                    data=output_buffer,
                    file_name=f"{os.path.splitext(archivo_subido.name)[0]}_aki.mp3",
                    mime="audio/mpeg"
                )
            except Exception as e:
                st.error(f"Error al procesar: {e}")
