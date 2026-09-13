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

# ===== GENERAR VALORES AL ESTILO ROBLOX (3 decimales) =====
# Fórmula: pitch = 2^(n/24), n entero. 24 pasos = 1 octava, cada paso = cuarto de tono.
# Se redondea a 3 decimales (igual que la web original Nomen Audio).

def format_pitch(value):
    """Redondea a 3 decimales y elimina ceros innecesarios a la derecha.
    Ejemplos: 0.420 → '0.42' | 0.397 → '0.397' | 1.000 → '1' | 0.500 → '0.5'
    """
    rounded = round(value, 3)
    s = f"{rounded:.3f}".rstrip('0').rstrip('.')
    return s if s else "0"

# Generar tabla de valores (n, pitch_redondeado, texto)
N_MIN, N_MAX = -80, 24  # 0.1x a 2.0x aprox
QT_VALUES = []  # lista de dicts con n, pitch, texto
for n in range(N_MIN, N_MAX + 1):
    raw = 2 ** (n / 24)
    pitch = round(raw, 3)  # 🔑 3 decimales (igual que Roblox)
    QT_VALUES.append({
        "n": n,
        "pitch": pitch,
        "texto": format_pitch(pitch)
    })

# Default: n = -30 → pitch ≈ 0.42 (índice 50 dentro de la lista)
DEFAULT_IDX = 50  # n=-30

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
    st.caption("Mueve el círculo. **Cada paso = ×1.0293 (+2.93%)**, el patrón exacto de Roblox (24 pasos = 1 octava).")
    
    # Pasar los valores al HTML para que el slider avance con los mismos datos
    valores_js = "[" + ",".join([f'{{"n":{v["n"]},"pitch":{v["pitch"]},"texto":"{v["texto"]}"}}' for v in QT_VALUES]) + "]"
    
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
            min-width: 80px; text-align: center; color: white; text-shadow: 1px 1px 2px #000; border: 2px solid #000;
            font-family: monospace; font-size: 16px; }}
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
                <input type="range" id="pitchIdx" min="0" max="{len(QT_VALUES)-1}" step="1" value="{DEFAULT_IDX}">
                <span class="value" id="pitchValue">{QT_VALUES[DEFAULT_IDX]["texto"]}</span>
            </div>
            
            <div class="info" id="stepInfo"></div>
            <div class="math" id="mathInfo"></div>
        </div>
        
        <script>
            const VALUES = {valores_js};
            const audio = document.getElementById('audio');
            const pitchIdx = document.getElementById('pitchIdx');
            const pitchValue = document.getElementById('pitchValue');
            const stepInfo = document.getElementById('stepInfo');
            const mathInfo = document.getElementById('mathInfo');
            
            audio.preservesPitch = false;
            audio.mozPreservesPitch = false;
            audio.webkitPreservesPitch = false;
            audio.msPreservesPitch = false;
            
            function applyPitch() {{
                const idx = parseInt(pitchIdx.value);
                const v = VALUES[idx];
                const pitchVal = v.pitch;
                audio.preservesPitch = false;
                audio.mozPreservesPitch = false;
                audio.webkitPreservesPitch = false;
                audio.msPreservesPitch = false;
                audio.playbackRate = 1 / pitchVal;
                pitchValue.textContent = v.texto;
                stepInfo.innerHTML = '📊 Paso <b>n = ' + v.n + '</b> · Pitch = <b>' + v.texto + '</b> · PlaybackRate = <b>' + (1/pitchVal).toFixed(4) + '</b>';
                mathInfo.innerHTML = '🧮 pitch = 2^(' + v.n + '/24)  |  Paso: ×1.0293 (+2.93%)  |  24 pasos = 1 octava';
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
    <p style="margin: 5px 0;"><b>n</b> = número entero. Se redondea a <b>3 decimales</b> (como en la web original).</p>
    <ul style="margin: 10px 0;">
    <li>Cada paso multiplica por <b>2<sup>(1/24)</sup> ≈ 1.0293</b> (+2.93%)</li>
    <li><b>24 pasos</b> = 1 octava = ×2 (o ×0.5)</li>
    <li>Cada paso = <b>1 cuarto de tono</b> musical</li>
    </ul>
    <p style="margin: 5px 0;">Tus valores exactos:</p>
    <ul style="margin: 10px 0; font-family: monospace; font-size: 13px;">
    <li>n = -33 → <b>0.386</b></li>
    <li>n = -32 → <b>0.397</b></li>
    <li>n = -31 → <b>0.408</b></li>
    <li>n = -30 → <b>0.42</b></li>
    <li>n = -29 → <b>0.433</b></li>
    <li>n =   8 → <b>1.26</b></li>
    <li>n =  17 → <b>1.634</b></li>
    <li>n =  18 → <b>1.682</b></li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== PASO 3: AJUSTE FINAL =====
    st.markdown("### 🎯 Paso 2: Ajusta el pitch final")
    st.caption("Cada paso es un cuarto de tono. El valor mostrado (3 decimales) es el que usarás en Roblox.")
    
    idx_usuario = st.slider(
        "Posición del slider",
        min_value=0,
        max_value=len(QT_VALUES) - 1,
        value=DEFAULT_IDX,
        step=1,
        key="idx_slider"
    )
    
    selected = QT_VALUES[idx_usuario]
    pitch_usuario = selected["pitch"]        # 🔑 3 decimales
    n_actual = selected["n"]
    texto_usuario = selected["texto"]
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("effectSpeed", texto_usuario)
    with col_info2:
        st.metric("Paso (n)", f"{n_actual}")
    with col_info3:
        st.metric("PlaybackRate", f"{1/pitch_usuario:.4f}")
    
    st.info(f"📌 **effectSpeed para Roblox = {texto_usuario}** (n = {n_actual})")
    
    st.markdown("---")
    
    # ===== PASO 4: CONVERSIÓN =====
    st.markdown("### 🔄 Paso 3: Convierte y descarga")
    
    if st.button("🔄 Convertir y descargar"):
        with st.spinner("Procesando audio completo..."):
            try:
                audio = AudioSegment.from_file(archivo_subido)
                duracion_original = len(audio) / 1000.0
                
                # Conversión matemáticamente perfecta:
                # Usamos el pitch de 3 decimales (el mismo que pondrás en Roblox)
                factor_conversion = 1.0 / pitch_usuario
                audio_pitch = cambiar_pitch(audio, factor_conversion)
                duracion_final = len(audio_pitch) / 1000.0
                
                output_buffer = audio_pitch.export(format="mp3", bitrate="192k")
                
                st.success("¡Conversión exitosa! 🎉")
                st.markdown("### 🔊 Así suena tu archivo convertido")
                st.audio(output_buffer, format="audio/mp3")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric(label="effectSpeed Roblox", value=texto_usuario)
                with col_b:
                    st.metric(label="Duración original", value=f"{duracion_original:.1f}s")
                with col_c:
                    st.metric(label="Duración convertida", value=f"{duracion_final:.1f}s")
                
                # Verificación matemática
                verificacion = (1.0 / pitch_usuario) * pitch_usuario
                st.info(
                    f"📌 **Instrucciones para Roblox Studio:**\n\n"
                    f"1. Sube este MP3 a Roblox.\n"
                    f"2. Pon **effectSpeed = {texto_usuario}** en el Sound.\n"
                    f"3. Verificación: `{1/pitch_usuario:.4f} × {texto_usuario} = {verificacion:.4f}` → vuelve al original ✅"
                )
                
                st.download_button(
                    label="📥 Descargar Audio Convertido",
                    data=output_buffer,
                    file_name=f"{os.path.splitext(archivo_subido.name)[0]}_aki_{texto_usuario}.mp3",
                    mime="audio/mpeg"
                )
            except Exception as e:
                st.error(f"Error al procesar: {e}")
