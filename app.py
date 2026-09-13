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
    
    /* 🔴 Alerta roja personalizada */
    .alerta-roja {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 50%, #dc2626 100%);
        border: 3px solid #ff0000;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 0 25px rgba(255, 0, 0, 0.7), inset 0 0 15px rgba(0, 0, 0, 0.5);
        animation: pulsoRojo 2s infinite;
    }
    .alerta-roja h3 {
        color: #ffffff !important;
        margin: 0 0 10px 0;
        font-size: 1.3em;
        text-shadow: 2px 2px 4px #000 !important;
    }
    .alerta-roja p {
        color: #ffe5e5 !important;
        margin: 8px 0;
        font-size: 1em;
        text-shadow: 1px 1px 3px #000 !important;
    }
    .alerta-roja .icono {
        font-size: 2em;
        margin-right: 10px;
    }
    @keyframes pulsoRojo {
        0%, 100% { box-shadow: 0 0 25px rgba(255, 0, 0, 0.7), inset 0 0 15px rgba(0, 0, 0, 0.5); }
        50% { box-shadow: 0 0 45px rgba(255, 0, 0, 1), inset 0 0 20px rgba(0, 0, 0, 0.7); }
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

# ===== CONSTANTES =====
MAX_DURATION_SEC = 7 * 60  # 7 minutos (límite de Roblox)
DEFAULT_N = -29  # 🔑 n = -29 → pitch ≈ 0.433

# ===== GENERAR VALORES AL ESTILO ROBLOX (3 decimales) =====
def format_pitch(value):
    """Redondea a 3 decimales y elimina ceros innecesarios a la derecha."""
    rounded = round(value, 3)
    s = f"{rounded:.3f}".rstrip('0').rstrip('.')
    return s if s else "0"

N_MIN, N_MAX = -80, 24
QT_VALUES = []
for n in range(N_MIN, N_MAX + 1):
    raw = 2 ** (n / 24)
    pitch = round(raw, 3)
    QT_VALUES.append({
        "n": n,
        "pitch": pitch,
        "texto": format_pitch(pitch)
    })

# Default: n = -29 → pitch ≈ 0.433
DEFAULT_IDX = DEFAULT_N - N_MIN  # índice del default

def cambiar_pitch(audio, factor):
    """Cambia pitch Y velocidad juntos (efecto vinilo, sin preservar tono)."""
    nuevos_frames = int(audio.frame_rate * factor)
    if nuevos_frames < 1000 or nuevos_frames > 200000:
        raise ValueError(f"Factor fuera de rango: {factor}")
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": nuevos_frames
    }).set_frame_rate(audio.frame_rate)

def format_duracion(seg):
    """Convierte segundos a formato mm:ss"""
    m = int(seg // 60)
    s = int(seg % 60)
    return f"{m}:{s:02d}"

# ===== SUBIR ARCHIVO =====
archivo_subido = st.file_uploader("🎵 Arrastra tu canción aquí", type=["mp3", "wav", "ogg", "flac"])

if archivo_subido is not None:
    temp_path = f"/tmp/{archivo_subido.name}"
    with open(temp_path, "wb") as f:
        f.write(archivo_subido.getbuffer())
    
    audio_bytes = open(temp_path, "rb").read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    
    # Duración original
    audio_temporal = AudioSegment.from_file(temp_path)
    duracion_original = len(audio_temporal) / 1000.0
    
    st.markdown(f"### 📊 Duración original: **{format_duracion(duracion_original)}** ({duracion_original:.1f} seg)")
    
    # ===== PASO 1: REPRODUCTOR =====
    st.markdown("### 🎧 Paso 1: Escucha cómo quedará")
    st.caption("Mueve el círculo. **Cada paso = ×1.0293 (+2.93%)**, el patrón exacto de Roblox (24 pasos = 1 octava).")
    
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
    <p style="margin: 5px 0;"><b>n</b> = número entero. Se redondea a <b>3 decimales</b>.</p>
    <ul style="margin: 10px 0;">
    <li>Cada paso multiplica por <b>2<sup>(1/24)</sup> ≈ 1.0293</b> (+2.93%)</li>
    <li><b>24 pasos</b> = 1 octava = ×2 (o ×0.5)</li>
    <li>Cada paso = <b>1 cuarto de tono</b> musical</li>
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
    pitch_usuario = selected["pitch"]
    n_actual = selected["n"]
    texto_usuario = selected["texto"]
    
    # 🔑 Duración estimada después de conversión
    duracion_estimada = duracion_original * pitch_usuario
    
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.metric("effectSpeed", texto_usuario)
    with col_info2:
        st.metric("Paso (n)", f"{n_actual}")
    with col_info3:
        st.metric("Duración final estimada", format_duracion(duracion_estimada))
    
    st.info(f"📌 **effectSpeed para Roblox = {texto_usuario}** (n = {n_actual})")
    
    # ===== 🔴 ALERTA ROJA SI SUPERA 7 MINUTOS =====
    if duracion_estimada > MAX_DURATION_SEC:
        exceso = duracion_estimada - MAX_DURATION_SEC
        st.markdown(f"""
        <div class="alerta-roja">
            <h3><span class="icono">🚨</span> ¡ADVERTENCIA! El audio supera los 7 minutos</h3>
            <p><b>Duración original:</b> {format_duracion(duracion_original)}</p>
            <p><b>Duración con este pitch ({texto_usuario}):</b> {format_duracion(duracion_estimada)}</p>
            <p><b>Exceso sobre el límite:</b> {exceso:.1f} segundos ({exceso/60:.2f} min)</p>
            <hr style="border-color: #ff6666; margin: 12px 0;">
            <p>⚠️ <b>Roblox Studio solo acepta audios de hasta 7:00 minutos de duración.</b></p>
            <p>Si intentas subir este archivo, Roblox lo <b>rechazará automáticamente</b>.</p>
            <p>💡 <b>Solución:</b> Baja el pitch (valores más pequeños = audio más rápido = dura menos). Por ejemplo, elige un valor menor como <b>0.386</b> o <b>0.375</b> para que el audio se acelere más y quepa en los 7 minutos.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== PASO 4: CONVERSIÓN =====
    st.markdown("### 🔄 Paso 3: Convierte y descarga")
    
    if st.button("🔄 Convertir y descargar"):
        with st.spinner("Procesando audio completo..."):
            try:
                audio = AudioSegment.from_file(archivo_subido)
                
                # Conversión matemáticamente perfecta
                factor_conversion = 1.0 / pitch_usuario
                audio_pitch = cambiar_pitch(audio, factor_conversion)
                duracion_final = len(audio_pitch) / 1000.0
                
                output_buffer = audio_pitch.export(format="mp3", bitrate="192k")
                
                # ===== Verificación del límite de 7 minutos =====
                if duracion_final > MAX_DURATION_SEC:
                    st.markdown(f"""
                    <div class="alerta-roja">
                        <h3><span class="icono">🚨</span> ¡Conversión bloqueada por exceso de duración!</h3>
                        <p><b>Duración convertida:</b> {format_duracion(duracion_final)} ({duracion_final:.1f} seg)</p>
                        <p><b>Límite de Roblox:</b> 7:00 minutos (420 seg)</p>
                        <p>❌ Este archivo <b>NO será aceptado por Roblox Studio</b>.</p>
                        <p>💡 Elige un pitch más bajo (por ejemplo <b>0.386</b> o <b>0.375</b>) para que el audio dure menos.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.success(f"¡Conversión exitosa! 🎉 (Duración: {format_duracion(duracion_final)}, dentro del límite de Roblox ✅)")
                    st.markdown("### 🔊 Así suena tu archivo convertido")
                    st.audio(output_buffer, format="audio/mp3")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric(label="effectSpeed Roblox", value=texto_usuario)
                    with col_b:
                        st.metric(label="Duración original", value=format_duracion(duracion_original))
                    with col_c:
                        st.metric(label="Duración convertida", value=format_duracion(duracion_final))
                    
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
