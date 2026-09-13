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

# ===== ESTILOS =====
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, 
            #ffffff 0%, #f0f0f0 8%, #d0d0d0 20%, #909090 40%, 
            #505050 60%, #282828 80%, #0a0a0a 100%);
        background-attachment: fixed;
    }
    h1, h2, h3, h4, p, label, .stMarkdown, .stCaption, span, div, li {
        color: #ffffff !important;
        text-shadow: -1px -1px 0 #000, 1px -1px 0 #000,
            -1px 1px 0 #000, 1px 1px 0 #000,
            0px 0px 6px rgba(0,0,0,0.9) !important;
    }
    h1 { font-family: 'Arial Black', sans-serif; text-align: center; font-size: 2.5em !important; }
    .stFileUploader {
        background-color: rgba(26, 26, 26, 0.92);
        border: 2px dashed #8b5cf6;
        border-radius: 15px; padding: 20px;
        backdrop-filter: blur(5px);
    }
    .stButton > button {
        background-color: #8b5cf6; color: white !important;
        border-radius: 10px; border: 2px solid #000;
        padding: 10px 24px; font-weight: bold; width: 100%;
        text-shadow: 1px 1px 2px #000 !important; font-size: 16px;
    }
    .stButton > button:hover { background-color: #7c3aed; }
    .stSlider > div > div > div > div { background-color: #8b5cf6; }
    .stMetric {
        background-color: rgba(26, 26, 26, 0.92);
        border-radius: 10px; padding: 15px;
        border: 2px solid #8b5cf6;
    }
    audio { width: 100%; border-radius: 10px; }
    .stAlert {
        background-color: rgba(26, 26, 26, 0.92);
        border-radius: 10px; border: 2px solid #8b5cf6;
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

# ===== PATRÓN QUARTER-TONE (el de Roblox) =====
# Cada paso: pitch = 2^(n/24), donde n es entero
# 24 pasos = 1 octava (×2 o ×0.5). Cada paso = ×1.0293 (cuarto de tono)
N_MIN, N_MAX = -40, 24
STEPS_N = list(range(N_MIN, N_MAX + 1))  # 65 valores
QT_VALUES = [round(2 ** (n / 24), 4) for n in STEPS_N]

# Default: pitch 0.42 → n = -30 → índice 10
DEFAULT_INDEX = 10

def format_pitch(value):
    """Formatea el pitch eliminando ceros innecesarios a la derecha."""
    # Redondear a 4 decimales y eliminar ceros finales
    formatted = f"{value:.4f}".rstrip('0').rstrip('.')
    return formatted

def cambiar_pitch(audio, factor):
    """Cambia pitch Y velocidad juntos (efecto vinilo, sin preservar tono)."""
    nuevos_frames = int(audio.frame_rate * factor)
    if nuevos_frames < 1000 or nuevos_frames > 200000:
        raise ValueError(f"Factor fuera de rango: {factor}")
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": nuevos_frames
    }).set_frame_rate(audio.frame_rate)

# ===== SUBIR ARCHIVO =====
archivo_subido = st.file_uploader("🎵 Arrastra tu canción aquí", type=["mp3", "wav", "ogg", "flac"])

if archivo_subido is not None:
    temp_path = f"/tmp/{archivo_subido.name}"
    with open(temp_path, "wb") as f:
        f.write(archivo_subido.getbuffer())
    
    audio_bytes = open(temp_path, "rb").read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    
    # ===== PASO 1: REPRODUCTOR =====
    st.markdown("### 🎧 Paso 1: Escucha cómo quedará")
    st.caption("Mueve el círculo. **Cada paso = 1 cuarto de tono = ×1.0293**, el patrón exacto de Roblox.")
    
    html_player = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ background: transparent; font-family: Arial, sans-serif; margin: 0; padding: 10px; }}
        .player {{ background: rgba(26, 26, 26, 0.95); border-radius: 15px; padding: 20px; border: 2px solid #8b5cf6; }}
        audio {{ width: 100%; margin-bottom: 15px; }}
        .controls {{ display: flex; align-items: center; gap: 15px; margin-bottom: 10px; }}
        .controls label {{ color: #fff; font-size: 14px; white-space: nowrap; text-shadow: 1px 1px 2px #000; font-weight: bold; }}
        input[type=range] {{ flex: 1; -webkit-appearance: none; height: 8px; border-radius: 5px; background: #333; outline: none; }}
        input[type=range]::-webkit-slider-thumb {{
            -webkit-appearance: none; width: 24px; height: 24px; border-radius: 50%;
            background: #8b5cf6; cursor: pointer; border: 2px solid #000;
        }}
        .value {{ background: #8b5cf6; padding: 6px 14px; border-radius: 8px; font-weight: bold;
            min-width: 80px; text-align: center; color: white; text-shadow: 1px 1px 2px #000; border: 2px solid #000; }}
        .info {{ color: #fff; font-size: 12px; margin-top: 8px; text-shadow: 1px 1px 2px #000; }}
        .math {{ background: rgba(0,0,0,0.6); padding: 10px; border-radius: 8px; margin-top: 8px;
            font-family: monospace; font-size: 12px; color: #c4b5fd; border: 1px solid #8b5cf6; }}
    </style>
    </head>
    <body>
        <div class="player">
            <audio id="audio" controls src="data:audio/mp3;base64,{audio_b64}"></audio>
            
            <div class="controls">
                <label>🎚️ Pitch:</label>
                <input type="range" id="pitchIdx" min="0" max="64" step="1" value="{DEFAULT_INDEX}">
                <span class="value" id="pitchValue">{format_pitch(QT_VALUES[DEFAULT_INDEX])}</span>
            </div>
            
            <div class="info" id="stepInfo"></div>
            <div class="math" id="mathInfo"></div>
        </div>
        
        <script>
            const audio = document.getElementById('audio');
            const pitchIdx = document.getElementById('pitchIdx');
            const pitchValue = document.getElementById('pitchValue');
            const stepInfo = document.getElementById('stepInfo');
            const mathInfo = document.getElementById('mathInfo');
            
            audio.preservesPitch = false;
            audio.mozPreservesPitch = false;
            audio.webkitPreservesPitch = false;
            audio.msPreservesPitch = false;
            
            function formatPitch(val) {{
                // Redondear a 4 decimales y eliminar ceros finales
                let s = val.toFixed(4);
                s = s.replace(/0+$/, '');
                s = s.replace(/\\.$/, '');
                return s;
            }}
            
            function applyPitch() {{
                const idx = parseInt(pitchIdx.value);
                const n = idx - 40;
                const pitchVal = Math.pow(2, n / 24);
                audio.preservesPitch = false;
                audio.mozPreservesPitch = false;
                audio.webkitPreservesPitch = false;
                audio.playbackRate = 1 / pitchVal;
                pitchValue.textContent = formatPitch(pitchVal);
                stepInfo.innerHTML = '📊 Paso <b>n = ' + n + '</b> · Pitch = <b>' + formatPitch(pitchVal) + '</b> · PlaybackRate = <b>' + (1/pitchVal).toFixed(4) + '</b>';
                mathInfo.innerHTML = '🧮 pitch = 2^(' + n + '/24)  |  Paso: ×' + Math.pow(2, 1/24).toFixed(4) + ' (+2.93%)  |  24 pasos = 1 octava';
            }}
            
            applyPitch();
            pitchIdx.addEventListener('input', applyPitch);
        </script>
    </body>
    </html>
    """
    
    components.html(html_player, height=280)
    
    st.markdown("---")
    
    # ===== PASO 2: LA MATEMÁTICA =====
    st.markdown("### 🧮 El patrón matemático")
    
    st.markdown("""
    <div style="background: rgba(26,26,26,0.9); padding: 20px; border-radius: 12px; border: 2px solid #8b5cf6;">
    <p style="margin: 5px 0;">Los valores que Roblox acepta siguen esta fórmula:</p>
    <p style="font-size: 1.6em; text-align: center; font-weight: bold; margin: 15px 0; color: #c4b5fd;">
    pitch = 2<sup>(n/24)</sup>
    </p>
    <p style="margin: 5px 0;"><b>n</b> = número entero (índice del paso).</p>
    <ul style="margin: 10px 0;">
    <li>Cada paso multiplica por <b>2<sup>(1/24)</sup> ≈ 1.0293</b> (+2.93%)</li>
    <li><b>24 pasos</b> = 1 octava = ×2 (o ×0.5)</li>
    <li>Cada paso = <b>1 cuarto de tono</b> musical</li>
    </ul>
    <p style="margin: 5px 0;">Ejemplos (los tuyos):</p>
    <ul style="margin: 10px 0; font-family: monospace; font-size: 13px;">
    <li>n = -33 → 2<sup>(-33/24)</sup> = 0.3856 ≈ <b>0.386</b></li>
    <li>n = -32 → 2<sup>(-32/24)</sup> = 0.3969 ≈ <b>0.397</b></li>
    <li>n = -31 → 2<sup>(-31/24)</sup> = 0.4085 ≈ <b>0.408</b></li>
    <li>n = -30 → 2<sup>(-30/24)</sup> = 0.4204 ≈ <b>0.42</b></li>
    <li>n = -29 → 2<sup>(-29/24)</sup> = 0.4328 ≈ <b>0.433</b></li>
    <li>n =   8 → 2<sup>(8/24)</sup>  = 1.2599 ≈ <b>1.26</b></li>
    <li>n =  17 → 2<sup>(17/24)</sup> = 1.6339 ≈ <b>1.634</b></li>
    <li>n =  18 → 2<sup>(18/24)</sup> = 1.6818 ≈ <b>1.682</b></li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== PASO 3: AJUSTE FINAL =====
    st.markdown("### 🎯 Paso 2: Ajusta el pitch final")
    st.caption("Mueve el slider. Cada paso es un cuarto de tono (el patrón de Roblox).")
    
    idx_usuario = st.slider(
        "Índice (n)",
        min_value=0,
        max_value=64,
        value=DEFAULT_INDEX,
        step=1,
        key="idx_slider"
    )
    
    n_actual = idx_usuario - 40
    pitch_usuario = QT_VALUES[idx_usuario]
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("effectSpeed", f"{format_pitch(pitch_usuario)}")
    with col_info2:
        st.metric("Paso (n)", f"{n_actual}")
    with col_info3:
        st.metric("PlaybackRate", f"{1/pitch_usuario:.4f}")
    
    st.info(f"📌 **effectSpeed para Roblox = {format_pitch(pitch_usuario)}** (n = {n_actual})")
    
    st.markdown("---")
    
    # ===== PASO 4: CONVERSIÓN =====
    st.markdown("### 🔄 Paso 3: Convierte y descarga")
    
    if st.button("🔄 Convertir y descargar"):
        with st.spinner("Procesando audio completo..."):
            try:
                audio = AudioSegment.from_file(archivo_subido)
                duracion_original = len(audio) / 1000.0
                
                # Conversión matemáticamente correcta:
                # archivo se acelera a 1/pitch → al aplicar effectSpeed=pitch en Roblox, vuelve a 1.0
                factor_conversion = 1.0 / pitch_usuario
                audio_pitch = cambiar_pitch(audio, factor_conversion)
                duracion_final = len(audio_pitch) / 1000.0
                
                output_buffer = audio_pitch.export(format="mp3", bitrate="192k")
                
                st.success("¡Conversión exitosa! 🎉")
                st.markdown("### 🔊 Así suena tu archivo convertido")
                st.audio(output_buffer, format="audio/mp3")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric(label="effectSpeed Roblox", value=f"{format_pitch(pitch_usuario)}")
                with col_b:
                    st.metric(label="Duración original", value=f"{duracion_original:.1f}s")
                with col_c:
                    st.metric(label="Duración convertida", value=f"{duracion_final:.1f}s")
                
                st.info(
                    f"📌 **Instrucciones para Roblox Studio:**\n\n"
                    f"1. Sube este MP3 a Roblox.\n"
                    f"2. Pon **effectSpeed = {format_pitch(pitch_usuario)}** en el Sound.\n"
                    f"3. La canción sonará idéntica al original. ✅"
                )
                
                st.download_button(
                    label="📥 Descargar Audio Convertido",
                    data=output_buffer,
                    file_name=f"{os.path.splitext(archivo_subido.name)[0]}_aki_{format_pitch(pitch_usuario)}.mp3",
                    mime="audio/mpeg"
                )
            except Exception as e:
                st.error(f"Error al procesar: {e}")
