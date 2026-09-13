import streamlit as st
import streamlit.components.v1 as components
import os
from pydub import AudioSegment
import base64

# ... (todo el CSS y las constantes se mantienen igual) ...

# ===== SESSION STATE =====
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
    st.session_state.audio_name = None
    st.session_state.duracion_original = None
    st.session_state.pitch_seleccionado = QT_VALUES[DEFAULT_IDX]["pitch"]
    st.session_state.resultado_bytes = None  # 🔑 Guardamos los bytes del audio convertido
    st.session_state.resultado_info = None

# ... (leer parámetros de URL igual) ...

# ===== SUBIR ARCHIVO =====
archivo_subido = st.file_uploader("🎵 Arrastra tu canción aquí", type=["mp3", "wav", "ogg", "flac"])

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

# ===== REPRODUCTOR + BOTÓN + DESCARGA (TODO DENTRO DEL MISMO IFRAME) =====
if st.session_state.audio_data is not None:
    audio_b64 = base64.b64encode(st.session_state.audio_data).decode()
    duracion_original = st.session_state.duracion_original
    pitch_seleccionado = st.session_state.pitch_seleccionado
    texto_seleccionado = format_pitch(pitch_seleccionado)
    
    # 🔑 Si ya hay un resultado convertido, lo pasamos al iframe en base64
    resultado_b64 = ""
    if st.session_state.resultado_bytes is not None:
        resultado_b64 = base64.b64encode(st.session_state.resultado_bytes).decode()
    
    idx_inicial = DEFAULT_IDX
    for i, v in enumerate(QT_VALUES):
        if abs(v["pitch"] - pitch_seleccionado) < 0.0005:
            idx_inicial = i
            break
    
    valores_js = "[" + ",".join([f'{{"n":{v["n"]},"pitch":{v["pitch"]},"texto":"{v["texto"]}"}}' for v in QT_VALUES]) + "]"
    
    html_player = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        /* ... (mismos estilos que ya tienes) ... */
    </style>
    </head>
    <body>
        <div class="block">
            <div class="player-content">
                <audio id="audio" controls src="data:audio/mp3;base64,{audio_b64}"></audio>
                <!-- ... (sliders de pitch y volumen) ... -->
                <div class="info" id="infoDuracion"></div>
                <div id="alertaBox"></div>
            </div>
            
            <!-- 🔑 Botón de convertir -->
            <button class="convert-btn" id="convertBtn" onclick="convertir()">🔄 Convertir audio</button>
            
            <!-- 🔑 Sección de descarga (solo aparece después de convertir) -->
            <div id="resultadoBox" style="display:none; padding: 18px; border-top: 2px solid #6d28d9;">
                <h3 style="color:white; margin-bottom:10px;">✅ ¡Conversión exitosa!</h3>
                <audio id="audioConvertido" controls style="width:100%; margin-bottom:10px;"></audio>
                <a id="downloadLink" download style="display:block; width:100%; text-align:center; background: linear-gradient(135deg, #059669 0%, #10b981 100%); color:white; padding:14px; border-radius:12px; font-weight:bold; text-decoration:none; font-size:16px;">📥 Descargar Audio Convertido</a>
            </div>
        </div>
        
        <script>
            const VALUES = {valores_js};
            const DURACION_ORIGINAL = {duracion_original};
            const MAX_DUR = 420;
            const RESULTADO_B64 = "{resultado_b64}"; // 🔑 Bytes del audio convertido (si ya existe)
            
            // ... (funciones applyPitch, formatDuracion, etc.) ...
            
            // 🔑 Función de conversión
            function convertir() {{
                const btn = document.getElementById('convertBtn');
                btn.classList.add('loading');
                btn.textContent = '⏳ Convirtiendo...';
                
                const idx = parseInt(document.getElementById('pitchIdx').value);
                const pitchVal = VALUES[idx].pitch;
                
                // 🔑 Enviar al servidor para conversión usando fetch
                fetch(window.parent.location.href, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ pitch: pitchVal, filename: "{st.session_state.audio_name}" }})
                }})
                .then(response => response.blob())
                .then(blob => {{
                    // Crear URL del blob y mostrarlo
                    const url = URL.createObjectURL(blob);
                    document.getElementById('audioConvertido').src = url;
                    document.getElementById('downloadLink').href = url;
                    document.getElementById('downloadLink').download = "convertido_{texto_seleccionado}.mp3";
                    document.getElementById('resultadoBox').style.display = 'block';
                    btn.textContent = '🔄 Convertir de nuevo';
                    btn.classList.remove('loading');
                }})
                .catch(err => {{
                    alert('Error: ' + err);
                    btn.textContent = '🔄 Convertir audio';
                    btn.classList.remove('loading');
                }});
            }}
            
            // Si ya hay un resultado previo, mostrarlo al cargar
            if (RESULTADO_B64) {{
                const binary = atob(RESULTADO_B64);
                const bytes = new Uint8Array(binary.length);
                for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
                const blob = new Blob([bytes], {{ type: 'audio/mpeg' }});
                const url = URL.createObjectURL(blob);
                document.getElementById('audioConvertido').src = url;
                document.getElementById('downloadLink').href = url;
                document.getElementById('downloadLink').download = "convertido_{texto_seleccionado}.mp3";
                document.getElementById('resultadoBox').style.display = 'block';
            }}
            
            applyPitch();
            document.getElementById('pitchIdx').addEventListener('input', applyPitch);
            document.getElementById('volumeSlider').addEventListener('input', function() {{
                document.getElementById('audio').volume = parseFloat(this.value);
                document.getElementById('volumeValue').textContent = Math.round(this.value * 100) + '%';
            }});
        </script>
    </body>
    </html>
    """
    
    components.html(html_player, height=600)
    
    # ===== PROCESAR LA CONVERSIÓN DESDE PYTHON (API interna) =====
    # Esto es necesario porque pydub corre en Python, no en el navegador.
    # Para simplificar, usamos un botón oculto de Streamlit que se activa desde JS.
    # Pero como JS no puede hacer clic en botones de Streamlit directamente,
    # usamos un trigger de URL como antes, pero ahora guardamos el resultado en session_state.
    
    # (Esta parte se mantiene igual que antes, pero ahora el iframe también puede descargar el resultado)
