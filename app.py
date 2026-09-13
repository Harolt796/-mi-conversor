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
    
    h1, h2, h3, h4, p, label, .stMarkdown, .stCaption, span, div, li {
        color: #ffffff !important;
        text-shadow: 
            -1px -1px 0 #000,  
             1px -1px 0 #000,
            -1px  1px 0 #000,
             1px  1px 0 #000,
             0px  0px 6px rgba(0,0,0,0.9) !important;
    }
    
    h1 {
        font-family: 'Arial Black', sans-serif;
        text-align: center;
        font-size: 2.5em !important;
    }
    
    .stFileUploader {
        background-color: rgba(26, 26, 26, 0.92);
        border: 2px dashed #8b5cf6;
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(5px);
    }
    
    .stButton > button {
        background-color: #8b5cf6;
        color: white !important;
        border-radius: 10px;
        border: 2px solid #000;
        padding: 10px 16px;
        font-weight: bold;
        width: 100%;
        text-shadow: 1px 1px 2px #000 !important;
        font-size: 14px;
    }
    .stButton > button:hover {
        background-color: #7c3aed;
    }
    
    .stSlider > div > div > div > div {
        background-color: #8b5cf6;
    }
    
    .stMetric {
        background-color: rgba(26, 26, 26, 0.92);
        border-radius: 10px;
        padding: 15px;
        border: 2px solid #8b5cf6;
    }
    
    audio { width: 100%; border-radius: 10px; }
    
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
st.markdown("<p style='text-align: center;'>Sube tu canción, escucha cómo quedará, elige el pitch y descarga el archivo para Roblox.</p>", unsafe_allow_html=True)
st.markdown("---")

# ===== CONFIGURACIÓN =====
MAX_DURATION_SEC = 7 * 60
DEFAULT_PITCH = 0.794
PRESETS = [1.26, 1.634, 1.682, 0.433, 0.397, 0.42, 0.386, 0.375]

# Inicializar session state
if "pitch_valor" not in st.session_state:
    st.session_state.pitch_valor = DEFAULT_PITCH

# ===== FUNCIONES DE AUDIO =====
def cambiar_pitch(audio, factor):
    """
    Cambia pitch y velocidad juntos (efecto vinilo / Audacity).
    factor < 1 → audio MÁS LENTO y grave.
    factor > 1 → audio MÁS RÁPIDO y agudo.
    """
    nuevos_frames = int(audio.frame_rate * factor)
    if nuevos_frames < 1000 or nuevos_frames > 200000:
        raise ValueError(f"Factor fuera de rango: {factor}")
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
    # Guardar temporalmente
    temp_path = f"/tmp/{archivo_subido.name}"
    with open(temp_path, "wb") as f:
        f.write(archivo_subido.getbuffer())
    
    audio_bytes = open(temp_path, "rb").read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    
    # ===== PASO 1: REPRODUCTOR EN VIVO =====
    st.markdown("### 🎧 Paso 1: Escucha cómo quedará")
    st.caption("Mueve el slider mientras suena. **Pitch bajo = rápido y agudo (ardilla 🐿️).** **Pitch alto = lento y grave (ogro 👹).**")
    
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
                <input type="range" id="pitch" min="0.1" max="2.0" step="0.001" value="0.794">
                <span class="value" id="pitchValue">0.794</span>
            </div>
            
            <div class="info">
                💡 <b>Pitch bajo</b> = rápido y agudo (ardilla). <b>Pitch alto</b> = lento y grave.
                <br>Este número es el <b>effectSpeed</b> que pondrás en Roblox Studio.
            </div>
        </div>
        
        <script>
            const audio = document.getElementById('audio');
            const pitch = document.getElementById('pitch');
            const pitchValue = document.getElementById('pitchValue');
            
            // 🔑 CLAVE: Desactiva preservesPitch para cambiar VELOCIDAD + TONO juntos
            audio.preservesPitch = false;
            audio.mozPreservesPitch = false;
            audio.webkitPreservesPitch = false;
            audio.msPreservesPitch = false;
            
            function applyPitch() {{
                const pitchVal = parseFloat(pitch.value);
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
    
    # ===== PASO 2: PRESETS =====
    st.markdown("### 🎯 Paso 2: Valores predefinidos")
    st.caption("Haz clic en uno para seleccionarlo automáticamente como pitch final.")
    
    # Fila 1: primeros 4 presets
    cols1 = st.columns(4)
    for i, preset in enumerate(PRESETS[:4]):
        if cols1[i].button(f"⚡ {preset}", key=f"preset_a_{i}"):
            st.session_state.pitch_valor = preset
            st.rerun()
    
    # Fila 2: últimos 4 presets
    cols2 = st.columns(4)
    for i, preset in enumerate(PRESETS[4:]):
        if cols2[i].button(f"⚡ {preset}", key=f"preset_b_{i}"):
            st.session_state.pitch_valor = preset
            st.rerun()
    
    st.markdown("---")
    
    # ===== PASO 3: AJUSTE MANUAL Y CONVERSIÓN =====
    st.markdown("### 🎚️ Paso 3: Confirma y convierte")
    
    pitch_usuario = st.slider(
        "Pitch final para exportar",
        min_value=0.1,
        max_value=2.0,
        value=st.session_state.pitch_valor,
        step=0.001,
        key="pitch_slider"
    )
    
    st.info(f"📌 Pitch seleccionado actualmente: **{pitch_usuario:.3f}**")
    st.caption("Este mismo número es el que pondrás como `effectSpeed` en Roblox Studio.")
    
    if st.button("🔄 Convertir y descargar"):
        with st.spinner("Procesando audio completo..."):
            try:
                audio = AudioSegment.from_file(archivo_subido)
                
                # 🔑 CORRECCIÓN CLAVE: invertir para que el archivo se acelere cuando el pitch baja
                # pitch=0.794 → factor=1.26 → audio se acelera 1.26x (suena agudo, dura menos)
                factor_conversion = 1.0 / pitch_usuario
                audio_pitch = cambiar_pitch(audio, factor_conversion)
                
                # Ajustar si excede 7 minutos
                audio_final, speed_factor = ajustar_duracion(audio_pitch, MAX_DURATION_SEC)
                
                # El effectSpeed es exactamente el pitch que eligió el usuario
                effect_speed = round(pitch_usuario, 4)
                
                output_buffer = audio_final.export(format="mp3", bitrate="192k")
                
                st.success("¡Conversión exitosa! 🎉")
                
                st.markdown("### 🔊 Así suena tu archivo convertido (el que subirás a Roblox)")
                st.audio(output_buffer, format="audio/mp3")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric(label="EffectSpeed para Roblox", value=effect_speed)
                with col_b:
                    st.metric(label="Duración del archivo", value=f"{len(audio_final)/1000:.2f} seg")
                
                st.info(f"📌 En Roblox Studio, pon el **effectSpeed = {effect_speed}** para que la canción suene como el original.")
                
                st.download_button(
                    label="📥 Descargar Audio Convertido",
                    data=output_buffer,
                    file_name=f"{os.path.splitext(archivo_subido.name)[0]}_aki_{effect_speed}.mp3",
                    mime="audio/mpeg"
                )
            except Exception as e:
                st.error(f"Error al procesar: {e}")
