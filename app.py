import streamlit as st
import streamlit.components.v1 as components
import os
from pydub import AudioSegment
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
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
        text-shadow: 1px 1px 2px #000 !important;
        font-size: 16px;
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
MAX_DURATION_SEC = 7 * 60  # 7 minutos (solo para advertencia)

# ⚡ Únicos valores de effectSpeed que Roblox Studio acepta
PRESETS = [0.375, 0.386, 0.397, 0.42, 0.433, 1.26, 1.634, 1.682]
DEFAULT_PITCH = 0.42

# Inicializar session state
if "pitch_valor" not in st.session_state:
    st.session_state.pitch_valor = DEFAULT_PITCH

# ===== FUNCIONES =====
def cambiar_pitch(audio, factor):
    """
    Cambia pitch Y velocidad juntos (efecto vinilo, igual que Audacity).
    NO usa preservación de tono — la voz cambia con la velocidad.
    
    factor < 1 → audio más LENTO y grave.
    factor > 1 → audio más RÁPIDO y agudo.
    """
    nuevos_frames = int(audio.frame_rate * factor)
    if nuevos_frames < 1000 or nuevos_frames > 200000:
        raise ValueError(f"Factor fuera de rango: {factor}")
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": nuevos_frames
    }).set_frame_rate(audio.frame_rate)


# ===== SUBIR ARCHIVO =====
archivo_subido = st.file_uploader("🎵 Arrastra tu canción aquí", type=["mp3", "wav", "ogg", "flac"])

if archivo_subido is not None:
    # Guardar temporalmente
    temp_path = f"/tmp/{archivo_subido.name}"
    with open(temp_path, "wb") as f:
        f.write(archivo_subido.getbuffer())
    
    audio_bytes = open(temp_path, "rb").read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    
    # ===== PASO 1: REPRODUCTOR =====
    st.markdown("### 🎧 Paso 1: Escucha cómo quedará")
    st.caption("Elige cada valor en el menú y escucha cómo suena. **Pitch bajo = rápido y agudo (ardilla).** **Pitch alto = lento y grave.**")
    
    # Generar las opciones del selector
    opciones_html = ""
    for p in PRESETS:
        selected = " selected" if p == DEFAULT_PITCH else ""
        opciones_html += f'<option value="{p}"{selected}>{p}</option>'
    
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
            flex-wrap: wrap;
        }}
        .controls label {{
            color: #ffffff;
            font-size: 14px;
            white-space: nowrap;
            text-shadow: 1px 1px 2px #000;
            font-weight: bold;
        }}
        select {{
            flex: 1;
            min-width: 120px;
            padding: 10px;
            border-radius: 8px;
            background: #8b5cf6;
            color: white;
            border: 2px solid #000;
            font-weight: bold;
            font-size: 15px;
            cursor: pointer;
            text-shadow: 1px 1px 2px #000;
        }}
        select option {{
            background: #1a1a1a;
            color: white;
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
                <select id="pitchSelect">
                    {opciones_html}
                </select>
            </div>
            
            <div class="info">
                💡 Estos son los <b>únicos valores que Roblox Studio acepta</b>. 
                Elige uno, escúchalo, y ese mismo número será tu <b>effectSpeed</b> en Roblox.
            </div>
        </div>
        
        <script>
            const audio = document.getElementById('audio');
            const pitchSelect = document.getElementById('pitchSelect');
            
            // 🔑 CLAVE: desactivar preservesPitch → cambia VELOCIDAD + TONO juntos
            audio.preservesPitch = false;
            audio.mozPreservesPitch = false;
            audio.webkitPreservesPitch = false;
            audio.msPreservesPitch = false;
            
            function applyPitch() {{
                const pitchVal = parseFloat(pitchSelect.value);
                audio.preservesPitch = false;
                audio.mozPreservesPitch = false;
                audio.webkitPreservesPitch = false;
                audio.playbackRate = 1 / pitchVal;
            }}
            
            applyPitch();
            pitchSelect.addEventListener('change', applyPitch);
        </script>
    </body>
    </html>
    """
    
    components.html(html_player, height=250)
    
    st.markdown("---")
    
    # ===== PASO 2: ELECCIÓN FINAL =====
    st.markdown("### 🎯 Paso 2: Confirma el pitch para exportar")
    st.caption("Estos son los únicos valores válidos para Roblox Studio.")
    
    pitch_usuario = st.select_slider(
        "Pitch final (effectSpeed)",
        options=PRESETS,
        value=st.session_state.pitch_valor,
        key="pitch_select_slider"
    )
    
    st.info(f"📌 EffectSpeed seleccionado: **{pitch_usuario}** — este es el número exacto que pondrás en Roblox Studio.")
    
    st.markdown("---")
    
    # ===== PASO 3: CONVERSIÓN =====
    st.markdown("### 🔄 Paso 3: Convierte y descarga")
    
    if st.button("🔄 Convertir y descargar"):
        with st.spinner("Procesando audio completo..."):
            try:
                audio = AudioSegment.from_file(archivo_subido)
                duracion_original = len(audio) / 1000.0
                
                # 🔑 CONVERSIÓN CORRECTA:
                # El archivo debe estar a 1/pitch de velocidad para que
                # al aplicar effectSpeed=pitch en Roblox, vuelva al original.
                factor_conversion = 1.0 / pitch_usuario
                audio_pitch = cambiar_pitch(audio, factor_conversion)
                
                duracion_final = len(audio_pitch) / 1000.0
                
                # Advertencia si supera 7 minutos (sin aplicar speedup, eso rompería la conversión)
                if duracion_final > MAX_DURATION_SEC:
                    st.warning(
                        f"⚠️ El audio convertido durará **{duracion_final/60:.2f} minutos** "
                        f"(más de 7 min). Roblox podría rechazarlo. "
                        f"Prueba con un pitch más bajo (más rápido)."
                    )
                
                output_buffer = audio_pitch.export(format="mp3", bitrate="192k")
                
                st.success("¡Conversión exitosa! 🎉")
                
                # Preview del resultado final
                st.markdown("### 🔊 Así suena tu archivo convertido (el que subirás a Roblox)")
                st.audio(output_buffer, format="audio/mp3")
                
                # Métricas
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric(label="EffectSpeed para Roblox", value=pitch_usuario)
                with col_b:
                    st.metric(label="Duración original", value=f"{duracion_original:.1f}s")
                with col_c:
                    st.metric(label="Duración final", value=f"{duracion_final:.1f}s")
                
                st.info(
                    f"📌 **Instrucciones para Roblox Studio:**\n\n"
                    f"1. Sube este MP3 a Roblox.\n"
                    f"2. Configura el **effectSpeed = {pitch_usuario}**.\n"
                    f"3. La canción sonará exactamente como el original. ✅"
                )
                
                st.download_button(
                    label="📥 Descargar Audio Convertido",
                    data=output_buffer,
                    file_name=f"{os.path.splitext(archivo_subido.name)[0]}_aki_{pitch_usuario}.mp3",
                    mime="audio/mpeg"
                )
            except Exception as e:
                st.error(f"Error al procesar: {e}")
