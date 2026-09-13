import streamlit as st
import os
from pydub import AudioSegment
from pydub.effects import speedup

MAX_DURATION_SEC = 7 * 60
DEFAULT_PITCH = 0.794

def cambiar_pitch(audio, factor):
    nuevos_frames = int(audio.frame_rate * factor)
    if nuevos_frames < 1000:
        raise ValueError("El factor de pitch es demasiado bajo.")
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": nuevos_frames
    }).set_frame_rate(audio.frame_rate)

def ajustar_duracion(audio, max_seg=MAX_DURATION_SEC):
    duracion = len(audio) / 1000.0
    if duracion <= max_seg:
        return audio, 1.0
    factor = duracion / max_seg
    return speedup(audio, playback_speed=factor, chunk_size=150), factor

st.title("🎧 Nomen Audio Converter (NekoDJ Style)")
st.write("Sube tu canción, ajusta el pitch y descarga el archivo listo para Roblox.")

archivo_subido = st.file_uploader("Arrastra tu canción aquí", type=["mp3", "wav", "ogg", "flac"])

if archivo_subido is not None:
    pitch_usuario = st.slider("Pitch (Shift)", 0.5, 1.5, DEFAULT_PITCH, 0.001)
    
    if st.button("Convertir 🚀"):
        with st.spinner("Procesando audio..."):
            try:
                audio = AudioSegment.from_file(archivo_subido)
                audio_pitch = cambiar_pitch(audio, pitch_usuario)
                audio_final, speed_factor = ajustar_duracion(audio_pitch, MAX_DURATION_SEC)
                effect_speed = round(pitch_usuario * speed_factor, 4)
                output_buffer = audio_final.export(format="mp3", bitrate="192k")
                
                st.success("¡Conversión exitosa!")
                st.metric(label="EffectSpeed para NekoDJ", value=effect_speed)
                st.info(f"Duración final: {len(audio_final)/1000:.2f} segundos")
                st.download_button(
                    label="📥 Descargar Audio Convertido",
                    data=output_buffer,
                    file_name=f"{os.path.splitext(archivo_subido.name)[0]}_neko.mp3",
                    mime="audio/mpeg"
                )
            except Exception as e:
                st.error(f"Error al procesar: {e}")