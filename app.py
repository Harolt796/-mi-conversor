import streamlit as st
import streamlit.components.v1 as components
import os
from pydub import AudioSegment
import base64
import time

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
    audio { width: 100%; border-radius: 10px; }
    .stAlert {
        background-color: rgba(26, 26, 26, 0.92);
        border-radius: 10px; border: 2px solid #8b5cf6;
    }
    .alerta-roja {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 50%, #dc2626 100%);
        border: 3px solid #ff0000;
        border-radius: 15px; padding: 20px; margin: 15px 0;
        box-shadow: 0 0 25px rgba(255, 0, 0, 0.7);
        animation: pulsoRojo 2s infinite;
    }
    .alerta-roja h3 { color: #fff !important; margin: 0 0 10px 0; font-size: 1.3em; }
    .alerta-roja p { color: #ffe5e5 !important; margin: 8px 0; }
    @keyframes pulsoRojo {
        0%, 100% { box-shadow: 0 0 25px rgba(255, 0, 0, 0.7); }
        50% { box-shadow: 0 0 45px rgba(255, 0, 0, 1); }
    }
    .alerta-verde {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #10b981 100%);
        border: 3px solid #10b981; border-radius: 15px; padding: 15px; margin: 15px 0;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
    }
    .alerta-verde p { color: #fff !important; margin: 0; }
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
st.markdown("<p style='text-align: center;'>Sube tu canción, ajusta el pitch y volumen, y descarga el archivo para Roblox.</p>", unsafe_allow_html=True)

# ===== CONSTANTES =====
MAX_DURATION_SEC = 7 * 60
DEFAULT_N = -29

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

# ===== INICIALIZAR SESSION STATE =====
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
    st.session_state.audio_name = None
    st.session_state.duracion_original = None
    st.session_state.pitch_seleccionado = QT_VALUES[DEFAULT_IDX]["pitch"]
    st.session_state.last_convert_trigger = None
    st.session_state.resultado = None

# ===== LEER PARÁMETROS DE URL =====
pitch_url_str = st.query_params.get("aki_pitch", None)
if pitch_url_str is not None:
    try:
        st.session_state.pitch_seleccionado = float(pitch_url_str)
    except:
        pass

convert_trigger = st.query_params.get("aki_convert", None)

# ===== SUBIR ARCHIVO =====
archivo_subido = st.file_uploader("🎵 Arrastra tu canción aquí", type=["mp3", "wav", "ogg", "flac"])

if archivo_subido is not None:
    # Solo procesar si es un archivo nuevo
    if st.session_state.audio_name != archivo_subido.name:
        st.session_state.audio_data = archivo_subido.getvalue()
        st.session_state.audio_name = archivo_subido.name
        
        temp_path = f"/tmp/{archivo_subido.name}"
        with open(temp_path, "wb") as f:
            f.write(archivo_subido.getbuffer())
        audio_temporal = AudioSegment.from_file(temp_path)
        st.session_state.duracion_original = len(audio_temporal) / 1000.0
        st.session_state.resultado = None  # Reset

# ===== MOSTRAR REPRODUCTOR SI HAY AUDIO =====
if st.session_state.audio_data is not None:
    audio_b64 = base64.b64encode(st.session_state.audio_data).decode()
    duracion_original = st.session_state.duracion_original
    pitch_seleccionado = st.session_state.pitch_seleccionado
    texto_seleccionado = format_pitch(pitch_seleccionado)
    
    # Encontrar índice inicial
    idx_inicial = DEFAULT_IDX
    for i, v in enumerate(QT_VALUES):
        if abs(v["pitch"] - pitch_seleccionado) < 0.0005:
            idx_inicial = i
            break
    
    valores_js = "[" + ",".join([f'{{"n":{v["n"]},"pitch":{v["pitch"]},"texto":"{v["texto"]}"}}' for v in QT_VALUES]) + "]"
    
    # ===== REPRODUCTOR + BOTÓN EN UN SOLO IFRAME =====
    html_player = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        html, body {{ 
            background: transparent; 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 0;
            overflow: hidden;
        }}
        .block {{
            background: rgba(26, 26, 26, 0.95);
            border-radius: 15px;
            border: 2px solid #8b5cf6;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4);
        }}
        .player-content {{
            padding: 18px 18px 14px 18px;
        }}
        audio {{ width: 100%; margin-bottom: 12px; }}
        .row {{ display: flex; align-items: center; gap: 15px; margin-bottom: 10px; }}
        .row label {{ color: #fff; font-size: 14px; white-space: nowrap; text-shadow: 1px 1px 2px #000; font-weight: bold; min-width: 90px; }}
        input[type=range] {{ flex: 1; -webkit-appearance: none; height: 8px; border-radius: 5px; background: #333; outline: none; }}
        input[type=range]::-webkit-slider-thumb {{
            -webkit-appearance: none; width: 24px; height: 24px; border-radius: 50%;
            background: #8b5cf6; cursor: pointer; border: 2px solid #000;
        }}
        .value {{ background: #8b5cf6; padding: 6px 14px; border-radius: 8px; font-weight: bold;
            min-width: 80px; text-align: center; color: white; text-shadow: 1px 1px 2px #000; border: 2px solid #000;
            font-family: monospace; font-size: 15px; }}
        .info {{ color: #fff; font-size: 13px; margin-top: 8px; text-shadow: 1px 1px 2px #000; padding: 10px;
            background: rgba(0,0,0,0.5); border-radius: 8px; border-left: 4px solid #8b5cf6; }}
        .alerta {{ background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 50%, #dc2626 100%);
            border: 2px solid #ff0000; border-radius: 12px; padding: 12px; margin-top: 8px;
            color: white; text-shadow: 1px 1px 3px #000; animation: pulso 2s infinite; font-size: 13px; }}
        .ok {{ background: linear-gradient(135deg, #064e3b 0%, #10b981 100%);
            border: 2px solid #10b981; border-radius: 12px; padding: 10px; margin-top: 8px;
            color: white; text-shadow: 1px 1px 3px #000; font-size: 13px; }}
        
        /* 🔑 BOTÓN DENTRO DEL MISMO BLOQUE */
        .convert-btn {{
            display: block;
            width: 100%;
            background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
            color: white;
            border: none;
            border-top: 2px solid #6d28d9;
            padding: 16px 24px;
            font-weight: bold;
            font-size: 18px;
            font-family: Arial, sans-serif;
            text-shadow: 1px 1px 2px #000;
            cursor: pointer;
            transition: all 0.2s ease;
            box-sizing: border-box;
        }}
        .convert-btn:hover {{
            background: linear-gradient(135deg, #6d28d9 0%, #7c3aed 100%);
            box-shadow: inset 0 0 20px rgba(255,255,255,0.1);
        }}
        .convert-btn:active {{
            transform: scale(0.98);
        }}
        .convert-btn.loading {{
            background: linear-gradient(135deg, #4c1d95 0%, #5b21b6 100%);
            cursor: wait;
            opacity: 0.8;
        }}
        @keyframes pulso {{
            0%, 100% {{ box-shadow: 0 0 20px rgba(255, 0, 0, 0.6); }}
            50% {{ box-shadow: 0 0 40px rgba(255, 0, 0, 1); }}
        }}
    </style>
    </head>
    <body>
        <div class="block">
            <div class="player-content">
                <audio id="audio" controls src="data:audio/mp3;base64,{audio_b64}"></audio>
                
                <div class="row">
                    <label>🎚️ Pitch:</label>
                    <input type="range" id="pitchIdx" min="0" max="{len(QT_VALUES)-1}" step="1" value="{idx_inicial}">
                    <span class="value" id="pitchValue">{QT_VALUES[idx_inicial]["texto"]}</span>
                </div>
                
                <div class="row">
                    <label>🔊 Volumen:</label>
                    <input type="range" id="volumeSlider" min="0" max="1" step="0.01" value="1">
                    <span class="value" id="volumeValue">100%</span>
                </div>
                
                <div class="info" id="infoDuracion"></div>
                <div id="alertaBox"></div>
            </div>
            
            <button class="convert-btn" id="convertBtn" onclick="convertir()">🔄 Convertir audio</button>
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
            const alertaBox = document.getElementById('alertaBox');
            const convertBtn = document.getElementById('convertBtn');
            
            audio.preservesPitch = false;
            audio.mozPreservesPitch = false;
            audio.webkitPreservesPitch = false;
            audio.msPreservesPitch = false;
            
            function formatDuracion(seg) {{
                const m = Math.floor(seg / 60);
                const s = Math.floor(seg % 60);
                return m + ':' + String(s).padStart(2,'0');
            }}
            
            function syncPitchToURL(pitchVal) {{
                try {{
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('aki_pitch', pitchVal.toFixed(3));
                    window.parent.history.replaceState({{}}, '', url.toString());
                }} catch(e) {{}}
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
                infoDuracion.innerHTML = '⏱️ Original: <b>' + formatDuracion(DURACION_ORIGINAL) + '</b> &nbsp;→&nbsp; Con este pitch: <b>' + formatDuracion(durFinal) + '</b> &nbsp;·&nbsp; effectSpeed: <b>' + v.texto + '</b>';
                
                if (durFinal > MAX_DUR) {{
                    alertaBox.innerHTML = '<div class="alerta">⚠️ <b>Recomendación:</b> Con este pitch el audio durará <b>' + formatDuracion(durFinal) + '</b>. Roblox recomienda máximo <b>7:00</b>. Considera bajar el pitch (más rápido) para asegurar la aceptación.</div>';
                }} else {{
                    alertaBox.innerHTML = '<div class="ok">✅ Duración dentro del límite recomendado de Roblox (7:00).</div>';
                }}
                
                syncPitchToURL(pitchVal);
            }}
            
            volumeSlider.addEventListener('input', function() {{
                audio.volume = parseFloat(this.value);
                volumeValue.textContent = Math.round(this.value * 100) + '%';
            }});
            
            // 🔑 FUNCIÓN DE CONVERSIÓN: recarga el padre con el trigger
            function convertir() {{
                convertBtn.classList.add('loading');
                convertBtn.textContent = '⏳ Convirtiendo...';
                
                try {{
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('aki_pitch', VALUES[parseInt(pitchIdx.value)].pitch.toFixed(3));
                    url.searchParams.set('aki_convert', Date.now().toString());
                    window.parent.location.href = url.toString();
                }} catch(e) {{
                    alert('Error al convertir: ' + e);
                    convertBtn.classList.remove('loading');
                    convertBtn.textContent = '🔄 Convertir audio';
                }}
            }}
            
            applyPitch();
            pitchIdx.addEventListener('input', applyPitch);
        </script>
    </body>
    </html>
    """
    
    components.html(html_player, height=480)
    
    # ===== PROCESAR CONVERSIÓN SI SE ACTIVÓ =====
    if convert_trigger and convert_trigger != st.session_state.last_convert_trigger:
        st.session_state.last_convert_trigger = convert_trigger
        
        with st.spinner("Procesando audio completo..."):
            try:
                temp_path = f"/tmp/{st.session_state.audio_name}"
                audio = AudioSegment.from_file(temp_path)
                
                factor_conversion = 1.0 / pitch_seleccionado
                audio_pitch = cambiar_pitch(audio, factor_conversion)
                duracion_final = len(audio_pitch) / 1000.0
                output_buffer = audio_pitch.export(format="mp3", bitrate="192k")
                
                st.session_state.resultado = {
                    "buffer": output_buffer.getvalue() if hasattr(output_buffer, 'getvalue') else output_buffer,
                    "duracion_final": duracion_final,
                    "texto_pitch": texto_seleccionado,
                    "nombre": f"{os.path.splitext(st.session_state.audio_name)[0]}_aki_{texto_seleccionado}.mp3"
                }
            except Exception as e:
                st.error(f"Error al procesar: {e}")
    
    # ===== MOSTRAR RESULTADO =====
    if st.session_state.resultado is not None:
        res = st.session_state.resultado
        
        st.success(f"¡Conversión exitosa! 🎉 Duración final: {format_duracion(res['duracion_final'])}")
        
        if res["duracion_final"] > MAX_DURATION_SEC:
            st.markdown(f"""
            <div class="alerta-roja">
                <h3>⚠️ El audio convertido supera los 7 minutos</h3>
                <p><b>Duración convertida:</b> {format_duracion(res['duracion_final'])}</p>
                <p>Roblox podría rechazarlo. Considera un pitch más bajo. <b>Puedes intentar subirlo de todas formas.</b> 👍</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alerta-verde">
                <p>✅ <b>¡Perfecto!</b> El audio dura <b>{format_duracion(res['duracion_final'])}</b>, dentro del límite recomendado de Roblox.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 🔊 Así suena tu archivo convertido")
        st.audio(res["buffer"], format="audio/mp3")
        
        st.info(f"📌 **En Roblox Studio:** pon **effectSpeed = {res['texto_pitch']}** en el Sound.")
        
        st.download_button(
            label="📥 Descargar Audio Convertido",
            data=res["buffer"],
            file_name=res["nombre"],
            mime="audio/mpeg"
        )
