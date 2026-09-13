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
    /* Fondo con degradado pronunciado: blanco centro -> plomo -> negro bordes */
    .stApp {
        background: radial-gradient(circle at center, 
            #ffffff 0%, 
            #f0f0f0 8%,
            #d0d0d0 20%,
            #909090 40%, 
            #505050 60%, 
            #282828 80%,
            #0a0a0a 100%);
        background-attachment: fixed;
    }
    
    /* TODAS las letras blancas con borde negro para que se lean sobre fondo blanco */
    h1, h2, h3, h4, p, label, .stMarkdown, .stCaption, span, div, li {
        color: #ffffff !important;
        text-shadow: 
            -1px -1px 0 #000,  
             1px -1px 0 #000,
            -1px  1px 0 #000,
             1px  1px 0 #000,
             0px  0px 6px rgba(0,0,0,0.9) !important;
    }
    
    /* Título principal */
    h1 {
        font-family: 'Arial Black', sans-serif;
        text-align: center;
        font-size: 2.5em !important;
    }
    
    /* Caja de subida de archivos */
    .stFileUploader {
        background-color: rgba(26, 26, 26, 0.92);
        border: 2px dashed #8b5cf6;
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(5px);
    }
    
    /* Botones */
    .stButton > button {
        background-color: #8b5cf6;
        color: white;
        border-radius: 10px;
        border: 2px solid #000;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
        text-shadow: 1px 1px 2px #000;
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
        background-color: rgba(26, 26, 26, 0.92);
        border-radius: 10px;
        padding: 15px;
        border: 2px solid #8b5cf6;
    }
    
    /* Reproductor de audio */
    audio { width: 100%; border-radius: 10px; }
    
    /* Mensaje de éxito/info */
    .stAlert {
        background-color: rgba(26, 26, 26, 0.92);
        border-radius: 10px;
        border: 2px solid #8b5cf6;
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
st.markdown("<p style='text-align: center;'>Sube tu canción, escucha cómo quedará, ajusta el pitch y descarga el archivo para Roblox.</p>", unsafe_allow_html=True)
st.markdown("---")

# ===== CONFIGURACIÓN =====
MAX_DURATION_SEC = 7 * 60
DEFAULT_PITCH = 0.794

def cambiar_pitch(audio, factor):
    """Cambia pitch y velocidad al mismo tiempo (efecto vinilo, como Audacity).
    factor < 1 → suena más agudo y rápido (ardilla)
    factor > 1 → suena más grave y lento
    """
    nuevos_frames = int(audio.frame_rate * factor)
    if nuevos_frames < 1000:
        raise ValueError("El factor de pitch es demasiado bajo.")
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": nuevos_frames
    }).set_frame_rate(audio.frame_rate)

def ajustar_duracion(audio, max_seg=MAX_DURATION_SEC):
    """Si el audio dura más del máximo, lo acelera sin cambiar pitch."""
    duracion = len(audio) / 1000.0
    if duracion <= max_seg:
        return audio, 1.0
    factor = duracion / max_seg
    return speedup(audio, playback_speed=factor, chunk_size=150), factor

# ===== SUBIR ARCHIVO =====
archivo_subido = st.file_uploader("🎵 Arrastra tu canción aquí", type=["mp3", "wav", "ogg", "flac"])

if archivo_subido is not None:
    temp_path = f"/tmp/{archivo_subido.name}"
    with open(temp_path, "wb") as f:
        f.write(archivo_subido.getbuffer())
    
    audio_bytes = open(temp_path, "rb").read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    
    st.markdown("### 🎧 Paso 1: Escucha cómo quedará la canción")
    st.caption("Mueve el slider mientras suena. **Pitch bajo (0.4) = rápido y agudo (ardilla).** **Pitch alto (1.5) = lento y grave.**")
    
    # ===== REPRODUCTOR EN VIVO CON VELOCIDAD Y TONO =====
    html_player = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            background: transparent;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
        }}
        .player {{
            background: rgba(26, 26, 26, 0.95);
            border-radius: 15px;
            padding: 20px;
            border: 2px solid #8b5cf6;
        }}
        audio {{ width: 100%; margin-bottom: 15px; }}
        .controls {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
        }}
        .controls label {{
            color: #ffffff;
            font-size: 14px;
            white-space: nowrap;
            text-shadow: 1px 1px 2px #000;
            font-weight: bold;
        }}
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
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: #8b5cf6;
            cursor: pointer;
            border: 2px solid #000;
        }}
        .value {{
            background: #8b5cf6;
            padding: 6px 14px;
            border-radius: 8px;
            font-weight: bold;
            min-width: 80px;
            text-align: center;
            color: white;
            text-shadow: 1px 1px 2px #000;
            border: 2px solid #000;
        }}
        .info {{
            color: #ffffff;
            font-size: 12px;
            margin-top: 10px;
            text-shadow: 1px 1px 2px #000;
        }}
    </style>
    </head>
    <body>
        <div class="player">
            <audio id="audio" controls src="data:audio/mp3;base64,{audio_b64}"></audio>
            
            <div class="controls">
                <label>🎚️ Pitch:</label>
                <input type="range" id="pitch" min="0.05" max="2.0" step="0.001" value="0.794">
                <span class="value" id="pitchValue">0.794</span>
            </div>
            
            <div class="info">
                💡 <b>Pitch bajo (0.4)</b> = rápido y agudo (voz de ardilla 🐿️). <b>Pitch alto (1.5)</b> = lento y grave (voz de ogro 👹).
                <br>Ese número es el <b>effectSpeed</b> que pondrás en Roblox Studio.
            </div>
        </div>
        
        <script>
            const audio = document.getElementById('audio');
            const pitch = document.getElementById('pitch');
            const pitchValue = document.getElementById('pitchValue');
            
            // 🔑 CLAVE: Desactivar preservesPitch para que cambie VELOCIDAD + TONO juntos (efecto Audacity)
            audio.preservesPitch = false;
            audio.mozPreservesPitch = false;
            audio.webkitPreservesPitch = false;
            audio.msPreservesPitch = false;
            
            function applyPitch() {{
                const pitchVal = parseFloat(pitch.value);
                // Invertir: pitch bajo = playbackRate alto (rápido y agudo)
                audio.playbackRate = 1 / pitchVal;
                pitchValue.textContent = pitchVal.toFixed(3);
            }}
            
            applyPitch();
            pitch.addEventListener('input', applyPitch);
        </script>
    </body>
    </html>
    """
    
    components.html(html_player, height=270)
    
    st.markdown("---")
    st.markdown("### 🎚️ Paso 2: Confirma el pitch y convierte")
    st.caption("Cuando ya hayas escuchado cómo queda, confirma el número y presiona Convertir.")
    
    pitch_usuario = st.slider("Pitch final para exportar", 0.05, 2.0, DEFAULT_PITCH, 0.001)
    
    if st.button("🔄 Convertir y descargar"):
        with st.spinner("Procesando audio completo..."):
            try:
                audio = AudioSegment.from_file(archivo_subido)
                audio_pitch = cambiar_pitch(audio, pitch_usuario)
                audio_final, speed_factor = ajustar_duracion(audio_pitch, MAX_DURATION_SEC)
                effect_speed = round(pitch_usuario * speed_factor, 4)
                output_buffer = audio_final.export(format="mp3", bitrate="192k")
                
                st.success("¡Conversión exitosa! 🎉")
                
                st.markdown("### 🔊 Así suena tu archivo convertido (el que subirás a Roblox)")
                st.audio(output_buffer, format="audio/mp3")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(label="EffectSpeed para Roblox Studio", value=effect_speed)
                with col_b:
                    st.metric(label="Duración del archivo", value=f"{len(audio_final)/1000:.2f} seg")
                
                st.info(f"📌 En Roblox Studio, pon el effectSpeed en **{effect_speed}** para que la canción suene como el original.")
                
                st.download_button(
                    label="📥 Descargar Audio Convertido",
                    data=output_buffer,
                    file_name=f"{os.path.splitext(archivo_subido.name)[0]}_aki.mp3",
                    mime="audio/mpeg"
                )
            except Exception as e:
                st.error(f"Error al procesar: {e}")
