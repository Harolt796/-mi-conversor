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
    .alerta-roja .icono { font-size: 1.8em; margin-right: 8px; }
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
st.markdown("<p style='text-align: center;'>Sube tu canción, escucha cómo quedará, ajusta el pitch y volumen, y descarga el archivo para Roblox.</p>", unsafe_allow_html=True)
st.markdown("---")

# ===== CONSTANTES =====
MAX_DURATION_SEC = 7 * 60  # 7 minutos (límite recomendado de Roblox)
DEFAULT_N = -29  # pitch ≈ 0.433

# ===== GENERAR VALORES AL ESTILO ROBLOX =====
def format_pitch(value):
    rounded = round(value, 3)
    s = f"{rounded:.3f}".rstrip('0').rstrip('.')
    return s if s else "0"

N_MIN, N_MAX = -80, 24
QT_VALUES = []
for n in range(N_MIN, N_MAX + 1):
    raw = 2 ** (n / 24)
    pitch = round(raw, 3)
    QT_VALUES.append({"n": n, "pitch": pitch, "texto": format_pitch(pitch)})

DEFAULT_IDX = DEFAULT_N - N_MIN

def cambiar_pitch(audio, factor):
    """Cambia pitch Y velocidad juntos (efecto vinilo, sin preservar tono)."""
    nuevos_frames = int(audio.frame_rate * factor)
    if nuevos_frames < 1000 or nuevos_frames > 200000:
        raise ValueError(f"Factor fuera de rango: {factor}")
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": nuevos_frames
    }).set_frame_rate(audio.frame_rate)

def format_duracion(seg):
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
    
    audio_temporal = AudioSegment.from_file(temp_path)
    duracion_original = len(audio_temporal) / 1000.0
    
    st.markdown(f"**📊 Duración original:** {format_duracion(duracion_original)} ({duracion_original:.1f} seg)")
    
    # ===== REPRODUCTOR HTML CON PITCH + VOLUMEN + DURACIÓN + ALERTA =====
    valores_js = "[" + ",".join([f'{{"n":{v["n"]},"pitch":{v["pitch"]},"texto":"{v["texto"]}"}}' for v in QT_VALUES]) + "]"
    
    html_player = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{ background: transparent; font-family: Arial, sans-serif; margin: 0; padding: 10px; }}
        .player {{ background: rgba(26, 26, 26, 0.95); border-radius: 15px; padding: 20px; border: 2px solid #8b5cf6; }}
        audio {{ width: 100%; margin-bottom: 15px; }}
        .row {{ display: flex; align-items: center; gap: 15px; margin-bottom: 12px; }}
        .row label {{ color: #fff; font-size: 14px; white-space: nowrap; text-shadow: 1px 1px 2px #000; font-weight: bold; min-width: 90px; }}
        input[type=range] {{ flex: 1; -webkit-appearance: none; height: 8px; border-radius: 5px; background: #333; outline: none; }}
        input[type=range]::-webkit-slider-thumb {{
            -webkit-appearance: none; width: 24px; height: 24px; border-radius: 50%;
            background: #8b5cf6; cursor: pointer; border: 2px solid #000;
        }}
        .value {{ background: #8b5cf6; padding: 6px 14px; border-radius: 8px; font-weight: bold;
            min-width: 80px; text-align: center; color: white; text-shadow: 1px 1px 2px #000; border: 2px solid #000;
            font-family: monospace; font-size: 15px; }}
        .info {{ color: #fff; font-size: 13px; margin-top: 10px; text-shadow: 1px 1px 2px #000; padding: 12px;
            background: rgba(0,0,0,0.5); border-radius: 8px; border-left: 4px solid #8b5cf6; }}
        .alerta {{ background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 50%, #dc2626 100%);
            border: 3px solid #ff0000; border-radius: 12px; padding: 15px; margin-top: 10px;
            color: white; text-shadow: 1px 1px 3px #000; animation: pulso 2s infinite; font-size: 13px; }}
        @keyframes pulso {{
            0%, 100% {{ box-shadow: 0 0 20px rgba(255, 0, 0, 0.6); }}
            50% {{ box-shadow: 0 0 40px rgba(255, 0, 0, 1); }}
        }}
    </style>
    </head>
    <body>
        <div class="player">
            <audio id="audio" controls src="data:audio/mp3;base64,{audio_b64}"></audio>
            
            <div class="row">
                <label>🎚️ Pitch:</label>
                <input type="range" id="pitchIdx" min="0" max="{len(QT_VALUES)-1}" step="1" value="{DEFAULT_IDX}">
                <span class="value" id="pitchValue">{QT_VALUES[DEFAULT_IDX]["texto"]}</span>
            </div>
            
            <div class="row">
                <label>🔊 Volumen:</label>
                <input type="range" id="volumeSlider" min="0" max="1" step="0.01" value="1">
                <span class="value" id="volumeValue">100%</span>
            </div>
            
            <div class="info" id="infoDuracion"></div>
            <div class="alerta" id="alerta" style="display:none;"></div>
        </div>
        
        <script>
            const VALUES = {valores_js};
            const DURACION_ORIGINAL = {duracion_original};
            const MAX_DUR = 420;
            const audio = document.getElementById('audio');
            const pitchIdx = document.getElementById('pitchIdx');
            const pitchValue = document.getElementById('pitchValue');
            const volumeSlider = document.getElementById('volumeSlider');
            const volumeValue = document.getElementById('volumeValue');
            const infoDuracion = document.getElementById('infoDuracion');
            const alerta = document.getElementById('alerta');
            
            audio.preservesPitch = false;
            audio.mozPreservesPitch = false;
            audio.webkitPreservesPitch = false;
            audio.msPreservesPitch = false;
            
            function formatDuracion(seg) {{
                const m = Math.floor(seg / 60);
                const s = Math.floor(seg % 60);
                return m + ':' + String(s).padStart(2,'0');
            }}
            
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
                
                const durFinal = DURACION_ORIGINAL * pitchVal;
                infoDuracion.innerHTML = '⏱️ Duración original: <b>' + formatDuracion(DURACION_ORIGINAL) + '</b> &nbsp;→&nbsp; Con este pitch: <b>' + formatDuracion(durFinal) + '</b>';
                
                if (durFinal > MAX_DUR) {{
                    alerta.style.display = 'block';
                    alerta.innerHTML = '⚠️ <b>Recomendación:</b> Con este pitch, el audio durará <b>' + formatDuracion(durFinal) + '</b>. Roblox recomienda máximo <b>7:00</b> por canción. Considera usar un pitch más bajo (audio más rápido) si quieres asegurar la aceptación.';
                }} else {{
                    alerta.style.display = 'none';
                }}
            }}
            
            volumeSlider.addEventListener('input', function() {{
                audio.volume = parseFloat(this.value);
                volumeValue.textContent = Math.round(this.value * 100) + '%';
            }});
            
            applyPitch();
            pitchIdx.addEventListener('input', applyPitch);
        </script>
    </body>
    </html>
    """
    
    components.html(html_player, height=420)
    
    st.markdown("---")
    st.markdown("**🎚️ Confirma el pitch para convertir:**")
    
    # Slider de Streamlit que controla la conversión
    idx_usuario = st.slider(
        "Pitch para la conversión",
        min_value=0,
        max_value=len(QT_VALUES) - 1,
        value=DEFAULT_IDX,
        step=1,
        key="pitch_convert",
        label_visibility="collapsed"
    )
    
    selected = QT_VALUES[idx_usuario]
    pitch_usuario = selected["pitch"]
    texto_usuario = selected["texto"]
    n_actual = selected["n"]
    
    duracion_estimada = duracion_original * pitch_usuario
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("effectSpeed", texto_usuario)
    with col2:
        st.metric("Duración estimada", format_duracion(duracion_estimada))
    with col3:
        st.metric("Paso (n)", f"{n_actual}")
    
    # ===== 🔴 ALERTA ROJA RECOMENDACIÓN =====
    if duracion_estimada > MAX_DURATION_SEC:
        exceso = duracion_estimada - MAX_DURATION_SEC
        st.markdown(f"""
        <div class="alerta-roja">
            <h3><span class="icono">⚠️</span> Recomendación importante</h3>
            <p><b>Duración original:</b> {format_duracion(duracion_original)}</p>
            <p><b>Duración con este pitch ({texto_usuario}):</b> {format_duracion(duracion_estimada)}</p>
            <p><b>Exceso sobre 7:00:</b> {exceso:.0f} segundos ({exceso/60:.2f} min)</p>
            <hr style="border-color: #ff6666; margin: 12px 0;">
            <p>💡 <b>Roblox Studio recomienda máximo 7:00 minutos por audio.</b> Si el archivo dura más, <b>es posible que Roblox lo rechace</b> al subirlo.</p>
            <p>✅ <b>Sugerencia:</b> Prueba con un pitch más bajo (ej: <b>0.386</b> o <b>0.375</b>). Un pitch más bajo acelera más el audio y reduce su duración.</p>
            <p>📌 <b>Puedes intentar subirlo de todas formas</b>, pero esta es solo una recomendación para ahorrarte tiempo.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #10b981 100%);
            border: 3px solid #10b981; border-radius: 15px; padding: 15px; margin: 15px 0;
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.5);">
            <p style="color: #ffffff !important; text-shadow: 1px 1px 3px #000 !important; margin: 0;">
            ✅ <b>¡Perfecto!</b> El audio durará <b>{format_duracion(duracion_estimada)}</b>, dentro del límite recomendado de 7:00 de Roblox.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== BOTÓN CONVERTIR =====
    if st.button("🔄 Convertir audio"):
        with st.spinner("Procesando audio completo..."):
            try:
                audio = AudioSegment.from_file(archivo_subido)
                
                factor_conversion = 1.0 / pitch_usuario
                audio_pitch = cambiar_pitch(audio, factor_conversion)
                duracion_final = len(audio_pitch) / 1000.0
                
                output_buffer = audio_pitch.export(format="mp3", bitrate="192k")
                
                st.success(f"¡Conversión exitosa! 🎉 Duración final: {format_duracion(duracion_final)}")
                
                # Alerta si el resultado supera 7 min
                if duracion_final > MAX_DURATION_SEC:
                    st.markdown(f"""
                    <div class="alerta-roja">
                        <h3><span class="icono">⚠️</span> El audio convertido supera los 7 minutos</h3>
                        <p><b>Duración convertida:</b> {format_duracion(duracion_final)}</p>
                        <p>Roblox podría rechazarlo al subirlo. Considera usar un pitch más bajo para reducirlo.</p>
                        <p>Pero puedes intentar subirlo de todas formas. 👍</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("### 🔊 Así suena tu archivo convertido")
                st.audio(output_buffer, format="audio/mp3")
                
                st.info(f"📌 **En Roblox Studio:** pon **effectSpeed = {texto_usuario}** en el Sound.")
                
                st.download_button(
                    label="📥 Descargar Audio Convertido",
                    data=output_buffer,
                    file_name=f"{os.path.splitext(archivo_subido.name)[0]}_aki_{texto_usuario}.mp3",
                    mime="audio/mpeg"
                )
            except Exception as e:
                st.error(f"Error al procesar: {e}")
