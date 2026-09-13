st.markdown("""
    <style>
    /* Fondo con degradado radial (blanco centro -> gris oscuro bordes) */
    .stApp {
        background: radial-gradient(circle at center, #ffffff 0%, #d3d3d3 25%, #4a4a4a 65%, #0a0a0a 100%);
        background-attachment: fixed;
        color: #ffffff;
    }
    
    /* Título principal */
    h1 {
        color: #ffffff !important;
        font-family: 'Arial Black', sans-serif;
        text-align: center;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
    }
    
    /* Subtítulos y textos */
    p, label, .stMarkdown {
        color: #f0f0f0 !important;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.6);
    }
    
    /* Caja de subida de archivos */
    .stFileUploader {
        background-color: rgba(26, 26, 26, 0.85);
        border: 2px dashed #8b5cf6;
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(5px);
    }
    
    /* Botones */
    .stButton > button {
        background-color: #8b5cf6;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #7c3aed;
    }
    
    /* Slider */
    .stSlider > div > div > div > div {
        background-color: #8b5cf6;
    }
    
    /* Caja de métricas */
    .stMetric {
        background-color: rgba(26, 26, 26, 0.85);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #8b5cf6;
        backdrop-filter: blur(5px);
    }
    
    /* Reproductor de audio */
    audio {
        width: 100%;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)
