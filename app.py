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
        background: #08080c;
    }
    [data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    footer {display: none;}
    #MainMenu {display: none;}
    
    /* Estilo personalizado para el file uploader */
    [data-testid="stFileUploader"] {
        background: transparent;
    }
    [data-testid="stFileUploader"] > section {
        background: rgba(20, 18, 30, 0.7) !important;
        border: 2px dashed #4c4a5e !important;
        border-radius: 14px !important;
        padding: 40px 20px !important;
        min-height: 180px;
    }
    [data-testid="stFileUploader"] > section:hover {
        border-color: #8b5cf6 !important;
    }
    [data-testid="stFileUploader"] button {
        background: #1a1826 !important;
        border: 1px solid #4c4a5e !important;
        color: #c4b5fd !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        padding: 8px 16px !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background: #2a2846 !important;
        border-color: #8b5cf6 !important;
    }
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] label {
        color: #e5e5e5 !important;
    }
    /* Ocultar la lista de archivos subidos por Streamlit */
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {
        display: none;
    }
    /* Textos generales */
    h1, h2, h3, h4, p, label, .stMarkdown, .stCaption, span, div {
        color: #ffffff !important;
    }
    audio { width: 100%; }
    .stAlert {
        background-color: rgba(26, 26, 26, 0.92);
        border-radius: 10px; border: 2px solid #8b5cf6;
    }
    .alerta-verde {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #10b981 100%);
        border: 3px solid #10b981; border-radius: 15px; padding: 15px; margin: 15px 0;
    }
    .alerta-verde p { color: #fff !important; margin: 0; }
    .alerta-roja {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 50%, #dc2626 100%);
        border: 3px solid #ff0000; border-radius: 15px; padding: 20px; margin: 15px 0;
        animation: pulsoRojo 2s infinite;
    }
    .alerta-roja h3 { color: #fff !important; margin: 0 0 10px 0; }
    .alerta-roja p { color: #ffe5e5 !important; margin: 8px 0; }
    @keyframes pulsoRojo {
        0%, 100% { box-shadow: 0 0 25px rgba(255, 0, 0, 0.7); }
        50% { box-shadow: 0 0 45px rgba(255, 0, 0, 1); }
    }
    </style>
""", unsafe_allow_html=True)

# ===== LOGO Y TÍTULO =====
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.png", width=180)
    except:
        st.markdown("<h1 style='text-align:center;'>😺</h1>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; padding: 10px 0 20px 0;'>
    <h1 style='font-family: Arial Black; font-size: 2.2em; margin:0;'>AKI <span style='color:#8b5cf6;'>AUDIO</span></h1>
    <p style='color:#888; font-family: monospace; font-size: 13px; letter-spacing: 2px; margin-top: 6px;'>
    AUDIO CONVERTER · V2 · ROBLOX READY
    </p>
</div>
""", unsafe_allow_html=True)

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

def semitonos_from_pitch(pitch):
    """Convierte el pitch al equivalente en semitonos (para mostrar +X.X st)."""
    import math
    st_val = 24 * math.log2(pitch)
    return st_val

# ===== SESSION STATE =====
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
    st.session_state.audio_name = None
    st.session_state.duracion_original = None
    st.session_state.pitch_seleccionado = QT_VALUES[DEFAULT_IDX]["pitch"]
    st.session_state.last_convert_trigger = None
    st.session_state.resultado_bytes = None
    st.session_state.resultado_info = None

# ===== LEER PARÁMETROS DE URL =====
pitch_url_str = st.query_params.get("aki_pitch", None)
if pitch_url_str is not None:
    try:
        st.session_state.pitch_seleccionado = float(pitch_url_str)
    except:
        pass

convert_trigger = st.query_params.get("aki_convert", None)

# ===== SUBIR ARCHIVO =====
archivo_subido = st.file_uploader(" ", type=["mp3", "wav", "ogg", "flac"], label_visibility="collapsed")

if archivo_subido is not None:
    if st.session_state.audio_name != archivo_subido.name:
        st.session_state.audio_data = archivo_subido.getvalue()
        st.session_state.audio_name = archivo_subido.name
        temp_path = f"/tmp/{archivo_subido.name}"
        with open(temp_path, "wb") as f:
            f.write(archivo_subido.getbuffer())
        audio_temporal = AudioSegment.from_file(temp_path)
        st.session_state.duracion_original = len(audio_temporal) / 1000.0
        st.session_state.resultado_bytes = None
        st.session_state.resultado_info = None

# ===== PROCESAR CONVERSIÓN SI SE ACTIVÓ =====
if convert_trigger and convert_trigger != st.session_state.last_convert_trigger and st.session_state.audio_data is not None:
    st.session_state.last_convert_trigger = convert_trigger
    
    with st.spinner("Convirtiendo audio..."):
        try:
            temp_path = f"/tmp/{st.session_state.audio_name}"
            audio = AudioSegment.from_file(temp_path)
            
            pitch_actual = st.session_state.pitch_seleccionado
            factor_conversion = 1.0 / pitch_actual
            audio_pitch = cambiar_pitch(audio, factor_conversion)
            duracion_final = len(audio_pitch) / 1000.0
            
            output_buffer = audio_pitch.export(format="mp3", bitrate="192k")
            bytes_finales = output_buffer.getvalue() if hasattr(output_buffer, 'getvalue') else bytes(output_buffer)
            
            st.session_state.resultado_bytes = bytes_finales
            st.session_state.resultado_info = {
                "duracion_final": duracion_final,
                "texto_pitch": format_pitch(pitch_actual),
                "nombre": f"{os.path.splitext(st.session_state.audio_name)[0]}_aki_{format_pitch(pitch_actual)}.mp3"
            }
        except Exception as e:
            st.error(f"Error al procesar: {e}")

# ===== REPRODUCTOR PRINCIPAL (dentro del iframe) =====
if st.session_state.audio_data is not None:
    audio_b64 = base64.b64encode(st.session_state.audio_data).decode()
    duracion_original = st.session_state.duracion_original
    pitch_seleccionado = st.session_state.pitch_seleccionado
    texto_seleccionado = format_pitch(pitch_seleccionado)
    
    # Info del resultado si existe
    resultado_b64 = ""
    resultado_nombre = ""
    if st.session_state.resultado_bytes is not None and st.session_state.resultado_info is not None:
        resultado_b64 = base64.b64encode(st.session_state.resultado_bytes).decode()
        resultado_nombre = st.session_state.resultado_info["nombre"]
    
    idx_inicial = DEFAULT_IDX
    for i, v in enumerate(QT_VALUES):
        if abs(v["pitch"] - pitch_seleccionado) < 0.0005:
            idx_inicial = i
            break
    
    valores_js = "[" + ",".join([f'{{"n":{v["n"]},"pitch":{v["pitch"]},"texto":"{v["texto"]}"}}' for v in QT_VALUES]) + "]"
    nombre_archivo = st.session_state.audio_name
    
    html_player = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700;900&display=swap');
        
        html, body {{
            background: transparent;
            font-family: 'Inter', Arial, sans-serif;
            margin: 0; padding: 0;
            overflow-x: hidden;
        }}
        
        .container {{
            background: #0a0a0f;
            border-radius: 16px;
            padding: 20px;
            border: 1px solid #1f1d2e;
        }}
        
        .card {{
            background: #0f0e17;
            border-radius: 14px;
            border: 1px solid #1f1d2e;
            overflow: hidden;
        }}
        
        /* Header del track */
        .track-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px 10px 20px;
            font-family: 'JetBrains Mono', monospace;
        }}
        .filename {{
            color: #ffffff;
            font-weight: 700;
            font-size: 14px;
        }}
        .status {{
            color: #5eead4;
            font-size: 11px;
            letter-spacing: 1px;
        }}
        .status .dur {{
            color: #888;
            margin-left: 8px;
        }}
        
        /* Fila de controles principales */
        .controls-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 20px;
        }}
        .btn {{
            background: #1a1826;
            color: #e5e5e5;
            border: 1px solid #2a2846;
            border-radius: 8px;
            padding: 8px 14px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .btn:hover {{
            background: #2a2846;
            border-color: #8b5cf6;
            color: #c4b5fd;
        }}
        .btn.active {{
            background: #8b5cf6;
            border-color: #8b5cf6;
            color: white;
        }}
        
        input[type=range] {{
            -webkit-appearance: none;
            appearance: none;
            height: 4px;
            border-radius: 2px;
            background: #2a2846;
            outline: none;
        }}
        input[type=range]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 14px; height: 14px;
            border-radius: 50%;
            background: #8b5cf6;
            cursor: pointer;
            border: 2px solid #0f0e17;
        }}
        input[type=range]::-moz-range-thumb {{
            width: 14px; height: 14px;
            border-radius: 50%;
            background: #8b5cf6;
            cursor: pointer;
            border: 2px solid #0f0e17;
        }}
        
        .pitch-slider {{
            flex: 1;
            margin: 0 8px;
        }}
        
        .pitch-info {{
            color: #888;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            white-space: nowrap;
        }}
        .pitch-info b {{
            color: #c4b5fd;
        }}
        
        /* Fila inferior */
        .bottom-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 20px 18px 20px;
            border-top: 1px solid #1a1826;
            margin-top: 8px;
        }}
        
        .vol-label {{
            color: #666;
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            letter-spacing: 1px;
        }}
        
        .vol-slider {{
            width: 100px;
        }}
        
        .vol-value {{
            color: #888;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            min-width: 32px;
        }}
        
        .format-group {{
            display: flex;
            gap: 4px;
            margin-left: auto;
        }}
        .fmt-btn {{
            background: transparent;
            color: #666;
            border: 1px solid #2a2846;
            border-radius: 6px;
            padding: 6px 10px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.15s;
        }}
        .fmt-btn.active {{
            background: #1a1826;
            color: white;
            border-color: #8b5cf6;
        }}
        
        .convert-btn {{
            background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.2s;
            margin-left: 8px;
        }}
        .convert-btn:hover {{
            background: linear-gradient(135deg, #6d28d9 0%, #7c3aed 100%);
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
        }}
        .convert-btn:disabled {{
            background: #2a2846;
            color: #666;
            cursor: wait;
        }}
        
        /* Audio oculto (controlado por JS) */
        #audioHidden {{ display: none; }}
        
        /* Alerta inline */
        .inline-alert {{
            padding: 10px 14px;
            border-radius: 8px;
            margin: 8px 20px 12px 20px;
            font-size: 12px;
            font-family: 'Inter', sans-serif;
        }}
        .inline-alert.ok {{
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid #10b981;
            color: #6ee7b7;
        }}
        .inline-alert.warn {{
            background: rgba(220, 38, 38, 0.15);
            border: 1px solid #dc2626;
            color: #fca5a5;
        }}
        
        /* Sección de resultado / descarga */
        .result-section {{
            margin-top: 12px;
            padding: 16px 20px;
            background: linear-gradient(135deg, rgba(6, 78, 59, 0.4) 0%, rgba(16, 185, 129, 0.15) 100%);
            border: 1px solid #10b981;
            border-radius: 12px;
        }}
        .result-section h3 {{
            color: #6ee7b7;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            margin: 0 0 12px 0;
            font-weight: 700;
        }}
        .download-link {{
            display: block;
            width: 100%;
            text-align: center;
            background: linear-gradient(135deg, #059669 0%, #10b981 100%);
            color: white;
            padding: 14px;
            border-radius: 10px;
            font-weight: 800;
            text-decoration: none;
            font-size: 14px;
            letter-spacing: 1px;
            box-sizing: border-box;
            transition: all 0.2s;
            border: none;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
        }}
        .download-link:hover {{
            background: linear-gradient(135deg, #047857 0%, #059669 100%);
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
        }}
        .result-info {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #a7f3d0;
            text-align: center;
            margin-top: 10px;
        }}
        
        /* Reproductor de resultado */
        #audioResult {{
            width: 100%;
            margin-bottom: 12px;
        }}
    </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div class="track-header">
                    <div class="filename">🎵 {nombre_archivo}</div>
                    <div class="status">READY<span class="dur">{format_duracion(duracion_original)}</span></div>
                </div>
                
                <div class="controls-row">
                    <button class="btn" id="previewBtn" onclick="togglePreview()">▶ PREVIEW</button>
                    <button class="btn active" id="manualBtn">MANUAL</button>
                    <input type="range" class="pitch-slider" id="pitchIdx" min="0" max="{len(QT_VALUES)-1}" step="1" value="{idx_inicial}">
                    <span class="pitch-info" id="pitchInfo"></span>
                </div>
                
                <div id="inlineAlert"></div>
                
                <div class="bottom-row">
                    <span class="vol-label">VOL</span>
                    <input type="range" class="vol-slider" id="volSlider" min="0" max="1" step="0.01" value="1">
                    <span class="vol-value" id="volValue">100%</span>
                    
                    <div class="format-group">
                        <button class="fmt-btn" onclick="setFormat('OGG')">OGG</button>
                        <button class="fmt-btn active" onclick="setFormat('MP3')">MP3</button>
                        <button class="fmt-btn" onclick="setFormat('WAV')">WAV</button>
                    </div>
                    
                    <button class="convert-btn" id="convertBtn" onclick="convertir()">CONVERT</button>
                </div>
                
                <audio id="audioHidden" src="data:audio/mp3;base64,{audio_b64}"></audio>
            </div>
            
            <div id="resultSection"></div>
        </div>
        
        <script>
            const VALUES = {valores_js};
            const DURACION_ORIGINAL = {duracion_original};
            const MAX_DUR = 420;
            const RESULTADO_B64 = "{resultado_b64}";
            const RESULTADO_NOMBRE = "{resultado_nombre}";
            
            const audio = document.getElementById('audioHidden');
            const pitchIdx = document.getElementById('pitchIdx');
            const pitchInfo = document.getElementById('pitchInfo');
            const volSlider = document.getElementById('volSlider');
            const volValue = document.getElementById('volValue');
            const inlineAlert = document.getElementById('inlineAlert');
            const previewBtn = document.getElementById('previewBtn');
            const convertBtn = document.getElementById('convertBtn');
            const resultSection = document.getElementById('resultSection');
            
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
                
                // 🔑 CRÍTICO: forzar preservesPitch=false cada vez
                audio.preservesPitch = false;
                audio.mozPreservesPitch = false;
                audio.webkitPreservesPitch = false;
                audio.msPreservesPitch = false;
                audio.playbackRate = 1 / pitchVal;
                
                const durFinal = DURACION_ORIGINAL * pitchVal;
                const semitonos = 24 * Math.log2(pitchVal);
                const semitonosStr = (semitonos >= 0 ? '+' : '') + semitonos.toFixed(1);
                const factor = (1 / pitchVal).toFixed(2);
                
                pitchInfo.innerHTML = '<b>' + semitonosStr + ' st</b> · ' + factor + 'x · value <b>' + v.texto + '</b> · out ' + formatDuracion(durFinal);
                
                if (durFinal > MAX_DUR) {{
                    inlineAlert.innerHTML = '<div class="inline-alert warn">⚠️ Con este pitch el audio durará <b>' + formatDuracion(durFinal) + '</b>. Roblox recomienda máximo 7:00.</div>';
                }} else {{
                    inlineAlert.innerHTML = '<div class="inline-alert ok">✅ Duración dentro del límite recomendado de Roblox (7:00).</div>';
                }}
            }}
            
            function togglePreview() {{
                if (audio.paused) {{
                    audio.play();
                    previewBtn.textContent = '⏸ PAUSA';
                }} else {{
                    audio.pause();
                    previewBtn.textContent = '▶ PREVIEW';
                }}
            }}
            
            audio.addEventListener('ended', function() {{
                previewBtn.textContent = '▶ PREVIEW';
            }});
            
            function setFormat(fmt) {{
                document.querySelectorAll('.fmt-btn').forEach(b => b.classList.remove('active'));
                event.target.classList.add('active');
            }}
            
            function convertir() {{
                convertBtn.disabled = true;
                convertBtn.textContent = '⏳...';
                try {{
                    const pitchVal = VALUES[parseInt(pitchIdx.value)].pitch;
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set('aki_pitch', pitchVal.toFixed(3));
                    url.searchParams.set('aki_convert', Date.now().toString());
                    window.parent.location.href = url.toString();
                }} catch(e) {{
                    alert('Error: ' + e);
                    convertBtn.disabled = false;
                    convertBtn.textContent = 'CONVERT';
                }}
            }}
            
            // Mostrar la sección de resultado si ya hay audio convertido
            function mostrarResultado() {{
                if (!RESULTADO_B64) return;
                
                // Convertir base64 a Blob
                const byteChars = atob(RESULTADO_B64);
                const byteNumbers = new Array(byteChars.length);
                for (let i = 0; i < byteChars.length; i++) {{
                    byteNumbers[i] = byteChars.charCodeAt(i);
                }}
                const byteArray = new Uint8Array(byteNumbers);
                const blob = new Blob([byteArray], {{ type: 'audio/mpeg' }});
                const url = URL.createObjectURL(blob);
                
                resultSection.innerHTML = `
                    <div class="result-section">
                        <h3>✅ ¡Conversión completada!</h3>
                        <audio id="audioResult" controls src="${{url}}"></audio>
                        <a class="download-link" id="dlLink" download="${{RESULTADO_NOMBRE}}">📥 DESCARGAR AUDIO CONVERTIDO</a>
                        <div class="result-info">${{RESULTADO_NOMBRE}}</div>
                    </div>
                `;
                
                const dlLink = document.getElementById('dlLink');
                dlLink.href = url;
                dlLink.download = RESULTADO_NOMBRE;
                dlLink.addEventListener('click', function(e) {{
                    // Fallback: forzar descarga
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = RESULTADO_NOMBRE;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                }});
            }}
            
            volSlider.addEventListener('input', function() {{
                audio.volume = parseFloat(this.value);
                volValue.textContent = Math.round(this.value * 100) + '%';
            }});
            
            pitchIdx.addEventListener('input', applyPitch);
            applyPitch();
            mostrarResultado();
        </script>
    </body>
    </html>
    """
    
    components.html(html_player, height=520)
    
    # ===== INFO EXTRA DEBAJO (opcional, con estilos coherentes) =====
    if st.session_state.resultado_info is not None:
        info = st.session_state.resultado_info
        if info["duracion_final"] > MAX_DURATION_SEC:
            st.markdown(f"""
            <div class="alerta-roja">
                <h3>⚠️ El audio convertido supera los 7 minutos</h3>
                <p><b>Duración convertida:</b> {format_duracion(info['duracion_final'])}</p>
                <p>Roblox podría rechazarlo. Puedes intentar subirlo de todas formas.</p>
            </div>
            """, unsafe_allow_html=True)
