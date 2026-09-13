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
    .stApp { background: #08080c; }
    [data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    footer {display: none;}
    #MainMenu {display: none;}
    [data-testid="stFileUploader"] { background: transparent; }
    [data-testid="stFileUploader"] > section {
        background: rgba(20, 18, 30, 0.7) !important;
        border: 2px dashed #4c4a5e !important;
        border-radius: 14px !important;
        padding: 40px 20px !important;
        min-height: 160px;
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
    }
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"] {
        display: none;
    }
    h1, h2, h3, h4, p, label, .stMarkdown, span, div { color: #fff !important; }
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
<div style='text-align:center; padding: 5px 0 15px 0;'>
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

def format_duracion(seg):
    m = int(seg // 60)
    s = int(seg % 60)
    return f"{m}:{s:02d}"

# ===== SESSION STATE =====
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
    st.session_state.audio_name = None
    st.session_state.duracion_original = None

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

# ===== REPRODUCTOR + CONVERSIÓN + DESCARGA (TODO DENTRO DEL IFRAME) =====
if st.session_state.audio_data is not None:
    audio_b64 = base64.b64encode(st.session_state.audio_data).decode()
    duracion_original = st.session_state.duracion_original
    nombre_archivo = st.session_state.audio_name
    nombre_base = os.path.splitext(nombre_archivo)[0]
    
    valores_js = "[" + ",".join([f'{{"n":{v["n"]},"pitch":{v["pitch"]},"texto":"{v["texto"]}"}}' for v in QT_VALUES]) + "]"
    
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
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 70%;
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
        
        .controls-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 20px;
        }}
        .btn {{
            background: #1a1826;
            color: #e5e5e5;
            border: 1px solid #2a2846;
            border-radius: 8px;
            padding: 10px 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.15s;
            white-space: nowrap;
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
        
        /* 🔑 SLIDER DE PITCH GRANDE */
        input[type=range].pitch-slider {{
            -webkit-appearance: none;
            appearance: none;
            flex: 1;
            height: 10px;
            border-radius: 5px;
            background: #2a2846;
            outline: none;
            margin: 0 12px;
            cursor: pointer;
        }}
        input[type=range].pitch-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #8b5cf6;
            cursor: grab;
            border: 3px solid #0f0e17;
            box-shadow: 0 0 10px rgba(139, 92, 246, 0.6);
        }}
        input[type=range].pitch-slider::-webkit-slider-thumb:active {{
            cursor: grabbing;
            background: #a78bfa;
            box-shadow: 0 0 20px rgba(139, 92, 246, 1);
        }}
        input[type=range].pitch-slider::-moz-range-thumb {{
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #8b5cf6;
            cursor: grab;
            border: 3px solid #0f0e17;
            box-shadow: 0 0 10px rgba(139, 92, 246, 0.6);
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
        
        .bottom-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 20px 18px 20px;
            border-top: 1px solid #1a1826;
            margin-top: 8px;
            flex-wrap: wrap;
        }}
        
        .vol-label {{
            color: #666;
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            letter-spacing: 1px;
        }}
        
        /* 🔑 SLIDER DE VOLUMEN GRANDE */
        input[type=range].vol-slider {{
            -webkit-appearance: none;
            appearance: none;
            width: 120px;
            height: 8px;
            border-radius: 4px;
            background: #2a2846;
            outline: none;
            cursor: pointer;
        }}
        input[type=range].vol-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: #8b5cf6;
            cursor: grab;
            border: 3px solid #0f0e17;
        }}
        input[type=range].vol-slider::-moz-range-thumb {{
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: #8b5cf6;
            cursor: grab;
            border: 3px solid #0f0e17;
        }}
        
        .vol-value {{
            color: #888;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            min-width: 38px;
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
            padding: 12px 22px;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.2s;
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
        
        #audioHidden {{ display: none; }}
        
        .inline-alert {{
            padding: 10px 14px;
            border-radius: 8px;
            margin: 8px 20px 12px 20px;
            font-size: 12px;
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
        
        .result-section {{
            margin-top: 12px;
            padding: 16px 20px;
            background: linear-gradient(135deg, rgba(6, 78, 59, 0.4) 0%, rgba(16, 185, 129, 0.15) 100%);
            border: 1px solid #10b981;
            border-radius: 12px;
        }}
        .result-section h3 {{
            color: #6ee7b7;
            font-size: 14px;
            margin: 0 0 12px 0;
            font-weight: 700;
        }}
        .download-link {{
            display: block;
            width: 100%;
            text-align: center;
            background: linear-gradient(135deg, #059669 0%, #10b981 100%);
            color: white !important;
            padding: 14px;
            border-radius: 10px;
            font-weight: 800;
            text-decoration: none;
            font-size: 14px;
            letter-spacing: 1px;
            box-sizing: border-box;
            cursor: pointer;
            border: none;
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
        
        #audioResult {{ width: 100%; margin-bottom: 12px; }}
        
        .progress-bar {{
            width: 100%;
            height: 6px;
            background: #2a2846;
            border-radius: 3px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #7c3aed, #8b5cf6);
            width: 0%;
            transition: width 0.2s;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/lamejs@1.2.1/lame.min.js"></script>
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
                    <button class="btn active">MANUAL</button>
                    <input type="range" class="pitch-slider" id="pitchIdx" min="0" max="{len(QT_VALUES)-1}" step="1" value="{DEFAULT_IDX}">
                    <span class="pitch-info" id="pitchInfo"></span>
                </div>
                
                <div id="inlineAlert"></div>
                
                <div class="bottom-row">
                    <span class="vol-label">VOL</span>
                    <input type="range" class="vol-slider" id="volSlider" min="0" max="1" step="0.01" value="1">
                    <span class="vol-value" id="volValue">100%</span>
                    
                    <div class="format-group">
                        <button class="fmt-btn">OGG</button>
                        <button class="fmt-btn active">MP3</button>
                        <button class="fmt-btn">WAV</button>
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
            const AUDIO_B64 = "{audio_b64}";
            const NOMBRE_BASE = "{nombre_base}";
            
            const audio = document.getElementById('audioHidden');
            const pitchIdx = document.getElementById('pitchIdx');
            const pitchInfo = document.getElementById('pitchInfo');
            const volSlider = document.getElementById('volSlider');
            const volValue = document.getElementById('volValue');
            const inlineAlert = document.getElementById('inlineAlert');
            const previewBtn = document.getElementById('previewBtn');
            const convertBtn = document.getElementById('convertBtn');
            const resultSection = document.getElementById('resultSection');
            
            // 🔑 Desactivar preservación de pitch para cambiar velocidad + tono juntos
            audio.preservesPitch = false;
            audio.mozPreservesPitch = false;
            audio.webkitPreservesPitch = false;
            audio.msPreservesPitch = false;
            
            // Buffer decodificado (se llena al cargar)
            let decodedBuffer = null;
            
            function formatDuracion(seg) {{
                const m = Math.floor(seg / 60);
                const s = Math.floor(seg % 60);
                return m + ':' + String(s).padStart(2,'0');
            }}
            
            function base64ToArrayBuffer(b64) {{
                const binary = atob(b64);
                const bytes = new Uint8Array(binary.length);
                for (let i = 0; i < binary.length; i++) {{
                    bytes[i] = binary.charCodeAt(i);
                }}
                return bytes.buffer;
            }}
            
            // Decodificar el audio al cargar
            (async function initDecode() {{
                try {{
                    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    const arrayBuffer = base64ToArrayBuffer(AUDIO_B64);
                    decodedBuffer = await audioCtx.decodeAudioData(arrayBuffer);
                    console.log('Audio decodificado:', decodedBuffer.duration.toFixed(1), 'seg');
                }} catch (e) {{
                    console.error('Error al decodificar:', e);
                }}
            }})();
            
            function applyPitch() {{
                const idx = parseInt(pitchIdx.value);
                const v = VALUES[idx];
                const pitchVal = v.pitch;
                
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
            
            // 🔑 CODIFICADOR MP3 CON LAMEJS
            function encodeMP3(audioBuffer, kbps) {{
                const sampleRate = audioBuffer.sampleRate;
                const numChannels = Math.min(2, audioBuffer.numberOfChannels);
                const mp3encoder = new lamejs.Mp3Encoder(numChannels, sampleRate, kbps);
                
                const sampleBlockSize = 1152;
                const mp3Data = [];
                
                const left = audioBuffer.getChannelData(0);
                const right = numChannels > 1 ? audioBuffer.getChannelData(1) : left;
                
                const leftInt = new Int16Array(left.length);
                const rightInt = new Int16Array(right.length);
                for (let i = 0; i < left.length; i++) {{
                    leftInt[i] = Math.max(-32768, Math.min(32767, left[i] * 32767));
                    rightInt[i] = Math.max(-32768, Math.min(32767, right[i] * 32767));
                }}
                
                for (let i = 0; i < leftInt.length; i += sampleBlockSize) {{
                    const leftChunk = leftInt.subarray(i, i + sampleBlockSize);
                    const rightChunk = rightInt.subarray(i, i + sampleBlockSize);
                    
                    let mp3buf;
                    if (numChannels === 2) {{
                        mp3buf = mp3encoder.encodeBuffer(leftChunk, rightChunk);
                    }} else {{
                        mp3buf = mp3encoder.encodeBuffer(leftChunk);
                    }}
                    
                    if (mp3buf.length > 0) {{
                        mp3Data.push(new Uint8Array(mp3buf));
                    }}
                }}
                
                const mp3buf = mp3encoder.flush();
                if (mp3buf.length > 0) {{
                    mp3Data.push(new Uint8Array(mp3buf));
                }}
                
                return new Blob(mp3Data, {{ type: 'audio/mp3' }});
            }}
            
            // 🔑 CONVERSIÓN 100% EN EL NAVEGADOR
            async function convertir() {{
                if (!decodedBuffer) {{
                    alert('El audio aún se está procesando. Espera unos segundos e intenta de nuevo.');
                    return;
                }}
                
                convertBtn.disabled = true;
                convertBtn.textContent = '⏳ PROCESANDO...';
                
                resultSection.innerHTML = `
                    <div class="result-section" style="background: rgba(139, 92, 246, 0.15); border-color: #8b5cf6;">
                        <h3 style="color: #c4b5fd;">⏳ Convirtiendo audio...</h3>
                        <div class="progress-bar"><div class="progress-fill" id="progFill"></div></div>
                        <div class="result-info" id="progText">Preparando...</div>
                    </div>
                `;
                
                try {{
                    const idx = parseInt(pitchIdx.value);
                    const pitchVal = VALUES[idx].pitch;
                    const factor = 1 / pitchVal;
                    
                    // Aplicar volumen master
                    const vol = parseFloat(volSlider.value);
                    
                    // Crear contexto offline
                    const newLength = Math.round(decodedBuffer.length / factor);
                    const offlineCtx = new OfflineAudioContext(
                        decodedBuffer.numberOfChannels,
                        newLength,
                        decodedBuffer.sampleRate
                    );
                    
                    const source = offlineCtx.createBufferSource();
                    source.buffer = decodedBuffer;
                    source.playbackRate.value = factor;
                    
                    // Gain node para el volumen
                    const gain = offlineCtx.createGain();
                    gain.gain.value = vol;
                    
                    source.connect(gain);
                    gain.connect(offlineCtx.destination);
                    source.start();
                    
                    document.getElementById('progText').textContent = 'Renderizando audio...';
                    document.getElementById('progFill').style.width = '30%';
                    
                    // Renderizar offline
                    const rendered = await offlineCtx.startRendering();
                    
                    document.getElementById('progText').textContent = 'Codificando MP3...';
                    document.getElementById('progFill').style.width = '70%';
                    
                    // Codificar a MP3 (en un setTimeout para no bloquear la UI)
                    setTimeout(() => {{
                        const mp3Blob = encodeMP3(rendered, 192);
                        const url = URL.createObjectURL(mp3Blob);
                        const durFinal = rendered.duration;
                        const nombreFinal = NOMBRE_BASE + '_aki_' + VALUES[idx].texto + '.mp3';
                        
                        document.getElementById('progFill').style.width = '100%';
                        
                        // Verificar duración
                        let alertaHTML = '';
                        if (durFinal > MAX_DUR) {{
                            alertaHTML = '<div class="inline-alert warn" style="margin: 10px 0;">⚠️ El audio dura ' + formatDuracion(durFinal) + ' (más de 7:00). Roblox podría rechazarlo.</div>';
                        }} else {{
                            alertaHTML = '<div class="inline-alert ok" style="margin: 10px 0;">✅ Duración: ' + formatDuracion(durFinal) + ' — dentro del límite de Roblox.</div>';
                        }}
                        
                        resultSection.innerHTML = `
                            <div class="result-section">
                                <h3>✅ ¡Conversión completada!</h3>
                                ${{alertaHTML}}
                                <audio id="audioResult" controls src="${{url}}"></audio>
                                <a class="download-link" id="dlLink">📥 DESCARGAR AUDIO CONVERTIDO</a>
                                <div class="result-info">${{nombreFinal}}</div>
                            </div>
                        `;
                        
                        // 🔑 Configurar el enlace de descarga correctamente
                        const dlLink = document.getElementById('dlLink');
                        dlLink.href = url;
                        dlLink.download = nombreFinal;
                        
                        // Fallback: forzar descarga con click manual
                        dlLink.addEventListener('click', function(e) {{
                            e.preventDefault();
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = nombreFinal;
                            a.style.display = 'none';
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                        }});
                        
                        convertBtn.disabled = false;
                        convertBtn.textContent = 'CONVERT';
                    }}, 100);
                    
                }} catch (e) {{
                    console.error(e);
                    resultSection.innerHTML = `
                        <div class="result-section" style="background: rgba(220, 38, 38, 0.15); border-color: #dc2626;">
                            <h3 style="color: #fca5a5;">❌ Error al convertir</h3>
                            <div class="result-info">${{e.message}}</div>
                        </div>
                    `;
                    convertBtn.disabled = false;
                    convertBtn.textContent = 'CONVERT';
                }}
            }}
            
            volSlider.addEventListener('input', function() {{
                audio.volume = parseFloat(this.value);
                volValue.textContent = Math.round(this.value * 100) + '%';
            }});
            
            pitchIdx.addEventListener('input', applyPitch);
            applyPitch();
        </script>
    </body>
    </html>
    """
    
    components.html(html_player, height=560)
