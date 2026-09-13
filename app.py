import streamlit as st
import streamlit.components.v1 as components
import os
import io
import mutagen
import base64

st.set_page_config(
    page_title="AKI Audio Converter",
    page_icon="😺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------------------------------
# LOGO EN BASE64 (para usarlo como marca de agua de fondo, sin servir archivos
# estáticos aparte)
# ----------------------------------------------------------------------------
_logo_b64 = None
try:
    with open("logo.png", "rb") as _f:
        _logo_b64 = base64.b64encode(_f.read()).decode()
except Exception:
    _logo_b64 = None

_logo_bg_css = ""
if _logo_b64:
    _logo_bg_css = f"""
.stApp::before {{
    content: "";
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image: url('data:image/png;base64,{_logo_b64}');
    background-repeat: no-repeat;
    background-position: center 6%;
    background-size: 780px;
    opacity: 0.05;
    filter: invert(1) blur(1px);
}}
"""

# ----------------------------------------------------------------------------
# ESTILOS GLOBALES DE LA PÁGINA (fuera del iframe)
# ----------------------------------------------------------------------------
CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
footer, #MainMenu {
    display: none !important;
}

.stApp {
    background: #07060a;
    position: relative;
    overflow-x: hidden;
    isolation: isolate;
    min-height: 100vh;
}

.stApp::after {
    content: "";
    position: absolute;
    inset: -6%;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(38% 32% at 18% 8%, rgba(139,92,246,0.20), transparent 60%),
        radial-gradient(34% 30% at 88% 14%, rgba(78,205,255,0.14), transparent 60%),
        radial-gradient(30% 26% at 10% 85%, rgba(240,166,58,0.08), transparent 60%),
        radial-gradient(45% 38% at 50% 100%, rgba(124,77,255,0.14), transparent 65%),
        radial-gradient(circle at 50% 0%, #17141f 0%, #0a090d 55%, #060506 100%);
    animation: bgBreathe 14s ease-in-out infinite alternate;
    transform-origin: center;
}

@keyframes bgBreathe {
    0% { transform: scale(1) translate(0, 0); }
    100% { transform: scale(1.06) translate(-1%, 1%); }
}

__LOGO_BG_CSS__

.block-container {
    padding-top: 2.2rem;
    max-width: 640px;
    position: relative;
    z-index: 1;
}

[data-testid="stFileUploader"] {
    position: relative;
    border: 1.5px dashed rgba(168, 130, 255, 0.4);
    border-radius: 20px;
    background: linear-gradient(160deg, rgba(139,92,246,0.06), rgba(255,255,255,0.015));
    backdrop-filter: blur(6px);
    padding: 2.4rem 1.4rem;
    min-height: 168px;
    transition: border-color .2s ease, background .2s ease;
    animation: dashFlow 5s ease-in-out infinite;
}

@keyframes dashFlow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(139,92,246,0); border-color: rgba(168,130,255,0.4); }
    50% { box-shadow: 0 0 26px 0 rgba(139,92,246,0.16); border-color: rgba(168,130,255,0.7); }
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(168, 130, 255, 0.85);
    background: linear-gradient(160deg, rgba(168,130,255,0.10), rgba(255,255,255,0.015));
}

[data-testid="stFileUploader"] section {
    background: transparent;
    border: none;
}

/* Reemplaza el texto en inglés del dropzone por instrucciones en español */
[data-testid="stFileUploaderDropzoneInstructions"] {
    font-size: 0 !important;
    display: flex !important;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}
[data-testid="stFileUploaderDropzoneInstructions"] svg { display: none; }
[data-testid="stFileUploaderDropzoneInstructions"]::before {
    content: "🎵";
    font-size: 2.4rem;
    line-height: 1;
    display: block;
    margin-bottom: 4px;
    filter: drop-shadow(0 0 10px rgba(139,92,246,0.5));
}
[data-testid="stFileUploaderDropzoneInstructions"]::after {
    content: "Arrastra tu canción aquí, o haz clic para buscarla\A MP3 · WAV · OGG · FLAC";
    white-space: pre-line;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    line-height: 1.6;
    text-align: center;
    color: rgba(235, 230, 245, 0.8);
}

[data-testid="stFileUploader"] button {
    font-size: 0 !important;
    background: linear-gradient(135deg, #8b5cf6, #6d3ff0) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.1rem !important;
    margin-top: 14px !important;
}
[data-testid="stFileUploader"] button::after {
    content: "Buscar archivo";
    font-size: 0.8rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
}

iframe {
    position: relative;
    z-index: 1;
}
</style>
"""

st.markdown(CSS_TEMPLATE.replace("__LOGO_BG_CSS__", _logo_bg_css), unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# ENCABEZADO / LOGO
# ----------------------------------------------------------------------------
if _logo_b64:
    st.markdown(
        f"""
        <div style="display:flex; justify-content:center; margin-bottom:-14px;">
            <div style="position:relative; width:118px; height:118px; display:flex;
                        align-items:center; justify-content:center;">
                <div style="position:absolute; inset:-20px; border-radius:50%;
                            background: radial-gradient(circle, rgba(139,92,246,0.45), transparent 70%);
                            filter: blur(8px); animation: akiPulse 3.2s ease-in-out infinite;"></div>
                <div style="position:absolute; inset:-2px; border-radius:50%;
                            background: conic-gradient(from 0deg, #8b5cf6, #4ecdff, #f0a63a, #8b5cf6);
                            animation: akiSpin 5s linear infinite; opacity:0.9;"></div>
                <div style="position:relative; width:100px; height:100px; border-radius:50%;
                            background: radial-gradient(circle, #1c1926 55%, #100e16 100%);
                            display:flex; align-items:center; justify-content:center;
                            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.06);">
                    <img src="data:image/png;base64,{_logo_b64}" width="66"
                         style="filter: invert(1) drop-shadow(0 0 10px rgba(200,182,255,0.55));" />
                </div>
            </div>
        </div>
        <style>
        @keyframes akiSpin {{ to {{ transform: rotate(360deg); }} }}
        @keyframes akiPulse {{
            0%, 100% {{ opacity: 0.55; transform: scale(1); }}
            50% {{ opacity: 0.9; transform: scale(1.08); }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div style='text-align:center; font-size:64px; margin-bottom:-10px;'>😺</div>",
        unsafe_allow_html=True
    )

st.markdown("""
<div style="text-align:center; margin-top:2px; margin-bottom:1.6rem;">
    <div style="font-family:'JetBrains Mono', monospace; font-weight:700; font-size:1.9rem;
                letter-spacing:2px; background: linear-gradient(135deg, #c9b6ff, #8b5cf6 60%, #5b34d6);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        AKI AUDIO
    </div>
    <div style="font-family:'JetBrains Mono', monospace; font-size:0.72rem; letter-spacing:3px;
                color:rgba(200,190,220,0.45); margin-top:2px; text-transform:uppercase;">
        Convertidor de tono y velocidad · Listo para Roblox
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# CONFIGURACIÓN DE VALORES DE PITCH (patrón cuarto de tono 2^(n/24))
# ----------------------------------------------------------------------------
MAX_DURATION_SEC = 7 * 60  # 420s recomendados por Roblox
DEFAULT_N = -29  # pitch ≈ 0.433


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


# ----------------------------------------------------------------------------
# ESTADO PERSISTENTE
# ----------------------------------------------------------------------------
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
if "audio_name" not in st.session_state:
    st.session_state.audio_name = None
if "duracion_original" not in st.session_state:
    st.session_state.duracion_original = 0

archivo_subido = st.file_uploader(
    " ", type=["mp3", "wav", "ogg", "flac"], label_visibility="collapsed"
)

if archivo_subido is not None:
    if st.session_state.audio_name != archivo_subido.name:
        st.session_state.audio_data = archivo_subido.getvalue()
        st.session_state.audio_name = archivo_subido.name
        # Lectura de metadatos únicamente (sin decodificar el audio ni usar ffmpeg)
        # esto hace que el menú aparezca casi al instante tras subir el archivo.
        try:
            info = mutagen.File(io.BytesIO(st.session_state.audio_data))
            st.session_state.duracion_original = info.info.length if info else 0
        except Exception:
            st.session_state.duracion_original = 0

# ----------------------------------------------------------------------------
# REPRODUCTOR + CONVERSOR (100% client-side)
# ----------------------------------------------------------------------------
if st.session_state.audio_data is not None:
    audio_b64 = base64.b64encode(st.session_state.audio_data).decode()
    duracion_original = st.session_state.duracion_original
    nombre_archivo = st.session_state.audio_name
    nombre_base = os.path.splitext(nombre_archivo)[0]
    valores_js = "[" + ",".join(
        [f'{{"n":{v["n"]},"pitch":{v["pitch"]},"texto":"{v["texto"]}"}}' for v in QT_VALUES]
    ) + "]"

    TEMPLATE = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; }
  body {
      margin: 0; padding: 0; background: transparent;
      font-family: 'Inter', sans-serif; color: #eae7f5;
  }
  :root {
      --accent: #8b5cf6;
      --accent-dim: rgba(139, 92, 246, 0.18);
      --accent-strong: #a882ff;
      --manual: #f0a63a;
      --manual-dim: rgba(240, 166, 58, 0.16);
      --danger: #ef4444;
      --ok: #22c55e;
      --line: rgba(255,255,255,0.08);
      --panel: rgba(255,255,255,0.035);
  }
  @property --aki-angle {
      syntax: '<angle>';
      initial-value: 0deg;
      inherits: false;
  }
  .container { padding: 10px 4px 14px 4px; }
  .card-halo {
      position: relative;
      border-radius: 22px;
      padding: 1.5px;
      background: conic-gradient(from var(--aki-angle), #8b5cf6, #4ecdff 30%, #f0a63a 55%, #8b5cf6 80%, #8b5cf6);
      animation: akiRotate 7s linear infinite;
      box-shadow: 0 16px 44px rgba(0,0,0,0.5);
  }
  @keyframes akiRotate { to { --aki-angle: 360deg; } }
  .card {
      position: relative;
      background: linear-gradient(160deg, #16141d 0%, #0e0c12 100%);
      border-radius: 20.5px;
      padding: 26px 24px 22px 24px;
      overflow: hidden;
  }
  .card::before {
      content: "";
      position: absolute; top: 0; left: 24px; right: 24px; height: 2px;
      background: linear-gradient(90deg, transparent, var(--accent-strong), transparent);
      opacity: 0.8;
  }
  .card::after {
      content: "";
      position: absolute; top: -60%; right: -30%; width: 60%; height: 160%;
      background: radial-gradient(circle, rgba(139,92,246,0.10), transparent 65%);
      pointer-events: none;
  }
  .track-header {
      display: flex; align-items: center; justify-content: space-between;
      margin-bottom: 18px; gap: 10px;
  }
  .filename {
      font-size: 0.95rem; font-weight: 600; color: #f2eefc;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 62%;
  }
  .status {
      font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; font-weight: 600;
      letter-spacing: 1.5px; color: var(--accent-strong);
      border: 1px solid rgba(139,92,246,0.35); background: var(--accent-dim);
      padding: 4px 10px; border-radius: 20px; display: flex; align-items: center; gap: 8px;
      white-space: nowrap;
  }
  .status .dur { color: rgba(230,225,245,0.55); font-weight: 500; }
  .controls-row { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
  .btn {
      font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.78rem;
      letter-spacing: 0.5px; padding: 9px 16px; border-radius: 12px;
      border: 1px solid var(--line); background: rgba(255,255,255,0.04); color: #d8d3ea;
      cursor: pointer; transition: all .15s ease; white-space: nowrap;
  }
  .btn:hover { background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.18); }
  #modeBtn.is-manual {
      background: var(--manual-dim); border-color: rgba(240,166,58,0.5); color: #ffcf8a;
  }
  #modeBtn.is-auto {
      background: var(--accent-dim); border-color: rgba(139,92,246,0.5); color: #d9c8ff;
  }

  .slider-wrap { display: flex; flex-direction: column; gap: 12px; margin-bottom: 6px; }
  .slider-row { display: flex; align-items: center; gap: 14px; }
  .slider-label {
      font-family: 'JetBrains Mono', monospace; font-size: 0.66rem; font-weight: 700;
      letter-spacing: 1.2px; color: rgba(220,213,240,0.55); width: 74px; flex-shrink: 0;
  }
  input[type=range] {
      -webkit-appearance: none; appearance: none; height: 8px; border-radius: 6px;
      background: rgba(255,255,255,0.08); outline: none; flex: 1; cursor: pointer;
  }
  input[type=range]::-webkit-slider-thumb {
      -webkit-appearance: none; width: 26px; height: 26px; border-radius: 50%;
      background: linear-gradient(145deg, #b298ff, #7c4dff);
      border: 3px solid #0e0c12; box-shadow: 0 2px 8px rgba(139,92,246,0.6);
      cursor: pointer; margin-top: -1px;
  }
  input[type=range]::-moz-range-thumb {
      width: 22px; height: 22px; border-radius: 50%;
      background: linear-gradient(145deg, #b298ff, #7c4dff);
      border: 3px solid #0e0c12; box-shadow: 0 2px 8px rgba(139,92,246,0.6); cursor: pointer;
  }
  input[type=range].manual-slider::-webkit-slider-thumb {
      background: linear-gradient(145deg, #ffcf8a, #f0a63a);
      box-shadow: 0 2px 8px rgba(240,166,58,0.55);
  }
  input[type=range].manual-slider::-moz-range-thumb {
      background: linear-gradient(145deg, #ffcf8a, #f0a63a);
      box-shadow: 0 2px 8px rgba(240,166,58,0.55);
  }
  .pitch-info {
      font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
      color: rgba(220,213,240,0.8); line-height: 1.6; padding: 10px 12px;
      background: var(--panel); border: 1px solid var(--line); border-radius: 12px; margin-top: 2px;
  }
  .pitch-info b { color: #f2eefc; }
  .inline-alert {
      margin-top: 10px; padding: 10px 13px; border-radius: 12px;
      font-size: 0.78rem; font-weight: 500; display: flex; align-items: center; gap: 8px;
  }
  .inline-alert.warn {
      background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.4); color: #ff9d9d;
  }
  .inline-alert.ok {
      background: rgba(34,197,94,0.10); border: 1px solid rgba(34,197,94,0.35); color: #8fe6ac;
  }
  .bottom-row {
      display: flex; align-items: center; gap: 14px; margin-top: 18px;
      padding-top: 16px; border-top: 1px solid var(--line); flex-wrap: wrap;
  }
  .vol-label {
      font-family: 'JetBrains Mono', monospace; font-size: 0.66rem; font-weight: 700;
      letter-spacing: 1px; color: rgba(220,213,240,0.55);
  }
  input[type=range].vol-slider { max-width: 120px; height: 6px; }
  input[type=range].vol-slider::-webkit-slider-thumb { width: 18px; height: 18px; }
  .vol-value {
      font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: rgba(220,213,240,0.7);
      width: 38px;
  }
  .format-group { display: flex; gap: 6px; margin-left: auto; }
  .fmt-btn {
      font-family: 'JetBrains Mono', monospace; font-size: 0.66rem; font-weight: 700;
      padding: 7px 10px; border-radius: 8px; border: 1px solid var(--line);
      background: rgba(255,255,255,0.03); color: rgba(220,213,240,0.4); cursor: not-allowed;
  }
  .fmt-btn.active {
      background: var(--accent-dim); border-color: rgba(139,92,246,0.5); color: #d9c8ff; cursor: default;
  }
  .convert-btn {
      font-family: 'Inter', sans-serif; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.5px;
      padding: 11px 22px; border-radius: 12px; border: none; cursor: pointer;
      background: linear-gradient(135deg, #a882ff, #7c4dff 60%, #5b34d6); color: white;
      box-shadow: 0 6px 18px rgba(124,77,255,0.4); transition: transform .12s ease, box-shadow .12s ease;
      width: 100%; margin-top: 14px;
  }
  .convert-btn:hover { transform: translateY(-1px); box-shadow: 0 8px 22px rgba(124,77,255,0.55); }
  .convert-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
  #audioHidden { display: none; }

  .result-section { margin-top: 14px; }
  .progress-bar {
      width: 100%; height: 8px; border-radius: 6px; background: rgba(255,255,255,0.08);
      overflow: hidden; margin-top: 6px;
  }
  .progress-fill {
      height: 100%; width: 40%; border-radius: 6px;
      background: linear-gradient(90deg, #7c4dff, #a882ff);
      animation: slide 1.1s ease-in-out infinite;
  }
  @keyframes slide {
      0% { margin-left: -40%; } 100% { margin-left: 100%; }
  }
  .result-card {
      margin-top: 12px; padding: 16px; border-radius: 14px;
      background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.3);
  }
  .result-title {
      font-weight: 700; font-size: 0.85rem; color: #8fe6ac; margin-bottom: 8px;
      display: flex; align-items: center; gap: 8px;
  }
  .result-info {
      font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
      color: rgba(220,240,225,0.75); line-height: 1.7; margin-bottom: 12px;
  }
  .download-link {
      display: inline-flex; align-items: center; gap: 8px; text-decoration: none;
      font-weight: 700; font-size: 0.8rem; padding: 10px 18px; border-radius: 10px;
      background: linear-gradient(135deg, #34d16f, #22c55e); color: #06210f;
      box-shadow: 0 4px 14px rgba(34,197,94,0.4);
  }
</style>
</head>
<body>
<div class="container">
 <div class="card-halo">
  <div class="card">
    <div class="track-header">
      <div class="filename">🎵 __NOMBRE_ARCHIVO__</div>
      <div class="status">LISTO<span class="dur">__DURACION_TXT__</span></div>
    </div>

    <div class="controls-row">
      <button class="btn" id="previewBtn" onclick="togglePreview()">▶ ESCUCHAR</button>
      <button class="btn is-auto" id="modeBtn" onclick="toggleMode()">MANUAL</button>
    </div>

    <div class="slider-wrap" id="autoSliderWrap" style="display:flex;">
      <div class="slider-row">
        <span class="slider-label">PITCH</span>
        <input type="range" id="pitchIdx" min="0" max="__LEN_VALUES__" step="1" value="__DEFAULT_IDX__">
      </div>
      <div class="pitch-info" id="pitchInfo"></div>
    </div>

    <div class="slider-wrap" id="manualSliderWrap" style="display:none;">
      <div class="slider-row">
        <span class="slider-label">VELOCIDAD</span>
        <input type="range" class="manual-slider" id="speedSlider" min="0.5" max="2" step="0.01" value="1">
      </div>
      <div class="slider-row">
        <span class="slider-label">TONO</span>
        <input type="range" class="manual-slider" id="toneSlider" min="-12" max="12" step="0.5" value="0">
      </div>
      <div class="pitch-info" id="manualInfo"></div>
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
    </div>

    <button class="convert-btn" id="convertBtn" onclick="convertir()">CONVERTIR Y DESCARGAR</button>

    <div id="resultSection" class="result-section"></div>

    <audio id="audioHidden" src="data:audio/mp3;base64,__AUDIO_B64__"></audio>
  </div>
 </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/lamejs@1.2.1/lame.min.js" defer></script>
<script>
const VALUES = __VALORES_JS__;
const DURACION_ORIGINAL = __DURACION_ORIGINAL__;
const MAX_DUR = __MAX_DUR__;
const AUDIO_B64 = "__AUDIO_B64__";
const NOMBRE_BASE = "__NOMBRE_BASE__";
const ORIGINAL_AUDIO_SRC = "data:audio/mp3;base64," + AUDIO_B64;

let mode = "auto";
let decodedBuffer = null;
let manualPreviewUrl = null;
let manualPreviewDirty = true;
let manualDebounceTimer = null;

const audioHidden = document.getElementById("audioHidden");
audioHidden.preservesPitch = false;
audioHidden.mozPreservesPitch = false;
audioHidden.webkitPreservesPitch = false;
audioHidden.msPreservesPitch = false;

audioHidden.addEventListener("pause", () => {
    document.getElementById("previewBtn").textContent = "▶ ESCUCHAR";
});
audioHidden.addEventListener("ended", () => {
    document.getElementById("previewBtn").textContent = "▶ ESCUCHAR";
});

function base64ToArrayBuffer(b64) {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return bytes.buffer;
}

(async function initDecode() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        decodedBuffer = await audioCtx.decodeAudioData(base64ToArrayBuffer(AUDIO_B64));
    } catch (e) {
        console.error("Error decodificando audio:", e);
    }
})();

function formatDuracion(seg) {
    const m = Math.floor(seg / 60);
    const s = Math.floor(seg % 60);
    return m + ":" + (s < 10 ? "0" : "") + s;
}

function updateFill(el) {
    const min = parseFloat(el.min), max = parseFloat(el.max), val = parseFloat(el.value);
    const pct = ((val - min) / (max - min)) * 100;
    const color = el.classList.contains("manual-slider") ? "#f0a63a" : "#8b5cf6";
    el.style.background = "linear-gradient(to right," + color + " 0%," + color + " " + pct + "%,rgba(255,255,255,0.08) " + pct + "%,rgba(255,255,255,0.08) 100%)";
}

function setAlert(elId, dentro) {
    const el = document.getElementById(elId);
    if (dentro) {
        el.innerHTML = "";
    } else {
        el.innerHTML = '<div class="inline-alert warn">⚠ Roblox recomienda un máximo de 7:00 minutos por audio. Este resultado supera ese límite y podría ser rechazado.</div>';
    }
}

function applyPitch() {
    const idx = parseInt(document.getElementById("pitchIdx").value);
    const v = VALUES[idx];
    const pitchVal = v.pitch;
    audioHidden.playbackRate = 1 / pitchVal;
    audioHidden.preservesPitch = false;
    audioHidden.mozPreservesPitch = false;
    audioHidden.webkitPreservesPitch = false;

    const semitonos = (v.n / 2).toFixed(1);
    const duracionSalida = DURACION_ORIGINAL * pitchVal;

    document.getElementById("pitchInfo").innerHTML =
        "PITCH: <b>" + v.texto + "</b> &nbsp;|&nbsp; SEMITONOS: <b>" + semitonos + "</b><br>" +
        "DURACIÓN ESTIMADA: <b>" + formatDuracion(duracionSalida) + "</b><br>" +
        "ROBLOX &middot; PlaybackSpeed = <b>" + v.texto + "</b> (para restaurar el audio original)";

    setAlert("inlineAlert", duracionSalida <= MAX_DUR);
    updateFill(document.getElementById("pitchIdx"));
}

function applyManualInfo() {
    const speedVal = parseFloat(document.getElementById("speedSlider").value);
    const toneVal = parseFloat(document.getElementById("toneSlider").value);
    const duracionSalida = DURACION_ORIGINAL / speedVal;

    document.getElementById("manualInfo").innerHTML =
        "VELOCIDAD: <b>" + speedVal.toFixed(2) + "x</b> &nbsp;|&nbsp; TONO: <b>" + (toneVal > 0 ? "+" : "") + toneVal + " st</b><br>" +
        "DURACIÓN ESTIMADA: <b>" + formatDuracion(duracionSalida) + "</b><br>" +
        "ROBLOX &middot; PlaybackSpeed = <b>1</b> (el tono y la velocidad ya quedan aplicados en el archivo)";

    setAlert("inlineAlert", duracionSalida <= MAX_DUR);
    updateFill(document.getElementById("speedSlider"));
    updateFill(document.getElementById("toneSlider"));
}

function toggleMode() {
    if (!audioHidden.paused) audioHidden.pause();
    audioHidden.loop = false;
    clearTimeout(manualDebounceTimer);
    mode = (mode === "auto") ? "manual" : "auto";

    const btn = document.getElementById("modeBtn");
    btn.textContent = (mode === "manual") ? "AUTOMÁTICO" : "MANUAL";
    btn.classList.toggle("is-manual", mode === "manual");
    btn.classList.toggle("is-auto", mode === "auto");

    document.getElementById("autoSliderWrap").style.display = (mode === "auto") ? "flex" : "none";
    document.getElementById("manualSliderWrap").style.display = (mode === "manual") ? "flex" : "none";

    audioHidden.src = ORIGINAL_AUDIO_SRC;
    audioHidden.playbackRate = 1;

    if (mode === "auto") {
        applyPitch();
    } else {
        applyManualInfo();
    }
}

function togglePreview() {
    const btn = document.getElementById("previewBtn");
    if (!audioHidden.paused) {
        audioHidden.pause();
        audioHidden.loop = false;
        clearTimeout(manualDebounceTimer);
        return;
    }
    if (mode === "auto") {
        audioHidden.loop = false;
        audioHidden.src = ORIGINAL_AUDIO_SRC;
        applyPitch();
        audioHidden.currentTime = 0;
        audioHidden.play();
        btn.textContent = "⏸ PAUSA";
    } else {
        previewManual();
    }
}

// ---------------- DSP: time-stretch (OLA) + pitch-shift independientes ----------------

function hannWindow(size) {
    const w = new Float32Array(size);
    for (let i = 0; i < size; i++) w[i] = 0.5 - 0.5 * Math.cos((2 * Math.PI * i) / (size - 1));
    return w;
}

function timeStretch(data, factor, frameSize) {
    frameSize = frameSize || 2048;
    const hopIn = Math.floor(frameSize / 4);
    const hopOut = Math.max(1, Math.round(hopIn * factor));
    const win = hannWindow(frameSize);
    const inputLen = data.length;
    const numFrames = Math.max(1, Math.floor((inputLen - frameSize) / hopIn));
    const outputLen = numFrames * hopOut + frameSize;
    const output = new Float32Array(outputLen);
    const norm = new Float32Array(outputLen);
    let inPos = 0, outPos = 0;
    for (let f = 0; f < numFrames; f++) {
        for (let i = 0; i < frameSize; i++) {
            const s = data[inPos + i] * win[i];
            output[outPos + i] += s;
            norm[outPos + i] += win[i] * win[i];
        }
        inPos += hopIn;
        outPos += hopOut;
    }
    for (let i = 0; i < outputLen; i++) {
        if (norm[i] > 1e-6) output[i] /= norm[i];
    }
    return output;
}

function resampleLinear(data, ratio) {
    const outputLen = Math.max(1, Math.floor(data.length / ratio));
    const output = new Float32Array(outputLen);
    for (let i = 0; i < outputLen; i++) {
        const srcPos = i * ratio;
        const i0 = Math.floor(srcPos);
        const i1 = Math.min(i0 + 1, data.length - 1);
        const frac = srcPos - i0;
        output[i] = data[i0] * (1 - frac) + data[i1] * frac;
    }
    return output;
}

function pitchShift(data, semitones) {
    if (Math.abs(semitones) < 0.001) return data;
    const ratio = Math.pow(2, semitones / 12);
    const resampled = resampleLinear(data, ratio);
    const restretched = timeStretch(resampled, ratio, 2048);
    const out = new Float32Array(data.length);
    const copyLen = Math.min(out.length, restretched.length);
    out.set(restretched.subarray(0, copyLen));
    return out;
}

function speedStretch(data, speedFactor) {
    if (Math.abs(speedFactor - 1) < 0.001) return data;
    const stretchFactor = 1 / speedFactor;
    return timeStretch(data, stretchFactor, 2048);
}

function processManual(channelsData, semitones, speedFactor) {
    return channelsData.map(ch => speedStretch(pitchShift(ch, semitones), speedFactor));
}

// ---------------- Codificación MP3 (lamejs) ----------------

function encodeMP3(audioBuffer, kbps) {
    const numChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const mp3encoder = new lamejs.Mp3Encoder(numChannels, sampleRate, kbps);
    const mp3Data = [];
    const blockSize = 1152;
    const left = audioBuffer.getChannelData(0);
    const right = numChannels > 1 ? audioBuffer.getChannelData(1) : left;

    const toInt16 = (arr) => {
        const out = new Int16Array(arr.length);
        for (let i = 0; i < arr.length; i++) {
            let s = Math.max(-1, Math.min(1, arr[i]));
            out[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        return out;
    };

    const left16 = toInt16(left);
    const right16 = numChannels > 1 ? toInt16(right) : left16;

    for (let i = 0; i < left16.length; i += blockSize) {
        const lChunk = left16.subarray(i, i + blockSize);
        const rChunk = right16.subarray(i, i + blockSize);
        const mp3buf = numChannels > 1
            ? mp3encoder.encodeBuffer(lChunk, rChunk)
            : mp3encoder.encodeBuffer(lChunk);
        if (mp3buf.length > 0) mp3Data.push(new Int8Array(mp3buf));
    }
    const end = mp3encoder.flush();
    if (end.length > 0) mp3Data.push(new Int8Array(end));

    return new Blob(mp3Data, { type: "audio/mp3" });
}

const MANUAL_PREVIEW_SECONDS = 10;

async function previewManual(isRefresh) {
    const btn = document.getElementById("previewBtn");
    if (!decodedBuffer) return;

    if (!isRefresh) {
        if (manualPreviewUrl && !manualPreviewDirty) {
            audioHidden.src = manualPreviewUrl;
            audioHidden.loop = true;
            audioHidden.playbackRate = 1;
            audioHidden.preservesPitch = true;
            audioHidden.currentTime = 0;
            audioHidden.play();
            btn.textContent = "⏸ PAUSA";
            return;
        }
        btn.textContent = "PROCESANDO...";
        btn.disabled = true;
        await new Promise(r => setTimeout(r, 20));
    }

    try {
        const sr = decodedBuffer.sampleRate;
        const maxSamples = Math.min(decodedBuffer.length, sr * MANUAL_PREVIEW_SECONDS);
        const numCh = decodedBuffer.numberOfChannels;
        const channels = [];
        for (let c = 0; c < numCh; c++) {
            channels.push(decodedBuffer.getChannelData(c).slice(0, maxSamples));
        }
        const semitones = parseFloat(document.getElementById("toneSlider").value);
        const speedVal = parseFloat(document.getElementById("speedSlider").value);
        const processed = processManual(channels, semitones, speedVal);
        const volVal = parseFloat(document.getElementById("volSlider").value);
        for (let c = 0; c < processed.length; c++) {
            for (let i = 0; i < processed[c].length; i++) processed[c][i] *= volVal;
        }
        const fakeBuffer = {
            numberOfChannels: numCh, sampleRate: sr, length: processed[0].length,
            getChannelData: (i) => processed[i]
        };
        const mp3Blob = encodeMP3(fakeBuffer, 128);
        const oldUrl = manualPreviewUrl;
        manualPreviewUrl = URL.createObjectURL(mp3Blob);
        manualPreviewDirty = false;

        const wasPlaying = !audioHidden.paused;
        audioHidden.src = manualPreviewUrl;
        audioHidden.loop = true;
        audioHidden.playbackRate = 1;
        audioHidden.preservesPitch = true;
        audioHidden.currentTime = 0;
        if (!isRefresh || wasPlaying) {
            audioHidden.play();
        }
        if (oldUrl) URL.revokeObjectURL(oldUrl);
        btn.textContent = "⏸ PAUSA";
    } catch (e) {
        console.error(e);
        document.getElementById("inlineAlert").innerHTML =
            '<div class="inline-alert warn">⚠ No se pudo generar la vista previa. Intenta mover el slider de nuevo.</div>';
        btn.textContent = "▶ ESCUCHAR";
    }
    if (!isRefresh) btn.disabled = false;
}

function scheduleManualRefresh() {
    if (mode !== "manual" || audioHidden.paused) return;
    clearTimeout(manualDebounceTimer);
    manualDebounceTimer = setTimeout(() => previewManual(true), 280);
}

async function convertir() {
    const btn = document.getElementById("convertBtn");
    btn.disabled = true;
    btn.textContent = "PROCESANDO...";
    document.getElementById("resultSection").innerHTML =
        '<div class="progress-bar"><div class="progress-fill"></div></div>';
    await new Promise(r => setTimeout(r, 60));

    try {
        const volVal = parseFloat(document.getElementById("volSlider").value);
        let renderedBufferLike;
        let sufijo, robloxTexto;

        if (mode === "auto") {
            const idx = parseInt(document.getElementById("pitchIdx").value);
            const pitchVal = VALUES[idx].pitch;
            const factor = 1 / pitchVal;
            const newLength = Math.floor(decodedBuffer.length / factor);
            const offlineCtx = new OfflineAudioContext(decodedBuffer.numberOfChannels, newLength, decodedBuffer.sampleRate);
            const source = offlineCtx.createBufferSource();
            source.buffer = decodedBuffer;
            source.playbackRate.value = factor;
            const gainNode = offlineCtx.createGain();
            gainNode.gain.value = volVal;
            source.connect(gainNode).connect(offlineCtx.destination);
            source.start();
            renderedBufferLike = await offlineCtx.startRendering();
            sufijo = VALUES[idx].texto;
            robloxTexto = "En Roblox Studio, pon <b>PlaybackSpeed = " + VALUES[idx].texto + "</b> para que el audio vuelva a sonar normal.";
        } else {
            const semitones = parseFloat(document.getElementById("toneSlider").value);
            const speedVal = parseFloat(document.getElementById("speedSlider").value);
            const numCh = decodedBuffer.numberOfChannels;
            const channels = [];
            for (let c = 0; c < numCh; c++) channels.push(decodedBuffer.getChannelData(c).slice());
            const processed = processManual(channels, semitones, speedVal);
            for (let c = 0; c < processed.length; c++) {
                for (let i = 0; i < processed[c].length; i++) processed[c][i] *= volVal;
            }
            renderedBufferLike = {
                numberOfChannels: numCh, sampleRate: decodedBuffer.sampleRate,
                length: processed[0].length, getChannelData: (i) => processed[i]
            };
            sufijo = "t" + semitones + "_v" + speedVal.toFixed(2);
            robloxTexto = "Este audio ya tiene el tono y la velocidad aplicados. En Roblox Studio deja <b>PlaybackSpeed = 1</b>.";
        }

        setTimeout(() => {
            const mp3Blob = encodeMP3(renderedBufferLike, 192);
            const url = URL.createObjectURL(mp3Blob);
            const nombreFinal = NOMBRE_BASE + "_" + sufijo + ".mp3";
            const durFinal = renderedBufferLike.length / renderedBufferLike.sampleRate;

            // Descarga automática apenas el archivo está listo (sin exigir un segundo clic)
            const autoLink = document.createElement("a");
            autoLink.href = url;
            autoLink.download = nombreFinal;
            document.body.appendChild(autoLink);
            autoLink.click();
            document.body.removeChild(autoLink);

            document.getElementById("resultSection").innerHTML =
                '<div class="result-card">' +
                  '<div class="result-title">✔ Descargado &middot; ' + formatDuracion(durFinal) + '</div>' +
                  '<div class="result-info">' + robloxTexto + '</div>' +
                  '<a class="download-link" id="dlLink" href="' + url + '" download="' + nombreFinal + '">⬇ Volver a descargar</a>' +
                  '<audio controls style="display:block; margin-top:10px; width:100%; height:34px;" src="' + url + '"></audio>' +
                '</div>';

            const dlLink = document.getElementById("dlLink");
            dlLink.addEventListener("click", function (ev) {
                ev.preventDefault();
                const a = document.createElement("a");
                a.href = url;
                a.download = nombreFinal;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            });

            btn.disabled = false;
            btn.textContent = "CONVERTIR Y DESCARGAR";
        }, 80);
    } catch (e) {
        console.error(e);
        btn.disabled = false;
        btn.textContent = "CONVERTIR Y DESCARGAR";
        document.getElementById("resultSection").innerHTML =
            '<div class="inline-alert warn">⚠ Ocurrió un error al convertir. Intenta de nuevo.</div>';
    }
}

document.getElementById("volSlider").addEventListener("input", function () {
    document.getElementById("volValue").textContent = Math.round(this.value * 100) + "%";
    updateFill(this);
    manualPreviewDirty = true;
    scheduleManualRefresh();
});
document.getElementById("pitchIdx").addEventListener("input", applyPitch);
document.getElementById("speedSlider").addEventListener("input", function () {
    manualPreviewDirty = true;
    applyManualInfo();
    scheduleManualRefresh();
});
document.getElementById("toneSlider").addEventListener("input", function () {
    manualPreviewDirty = true;
    applyManualInfo();
    scheduleManualRefresh();
});

applyPitch();
updateFill(document.getElementById("volSlider"));
</script>
</body>
</html>
"""

    html_player = (
        TEMPLATE
        .replace("__NOMBRE_ARCHIVO__", nombre_archivo)
        .replace("__DURACION_TXT__", format_duracion(duracion_original))
        .replace("__LEN_VALUES__", str(len(QT_VALUES) - 1))
        .replace("__DEFAULT_IDX__", str(DEFAULT_IDX))
        .replace("__VALORES_JS__", valores_js)
        .replace("__DURACION_ORIGINAL__", str(duracion_original))
        .replace("__MAX_DUR__", str(MAX_DURATION_SEC))
        .replace("__NOMBRE_BASE__", nombre_base)
        .replace("__AUDIO_B64__", audio_b64)
    )

    with st.spinner("🎧 Preparando el reproductor y las opciones de tono..."):
        components.html(html_player, height=760, scrolling=False)
