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
    
    /* 🔑 ELIMINAR TODOS LOS GAPS entre bloques verticales */
    div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* 🔑 ELIMINAR EL GAP ENTRE IFRAME Y BOTÓN */
    div[data-testid="stVerticalBlock"] > div:has(iframe) {
        margin-bottom: -14px !important;
        padding-bottom: 0 !important;
    }
    div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* 🔑 iframe sin margen inferior */
    iframe {
        display: block !important;
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
        border-bottom: none !important;
    }
    
    /* 🔑 Botón pegado al reproductor */
    div.stButton {
        margin-top: -14px !important;
        padding-top: 0 !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
        color: white !important;
        border-radius: 0 0 15px 15px !important;
        border: 2px solid #8b5cf6 !important;
        border-top: 1px solid #6d28d9 !important;
        padding: 16px 24px;
        font-weight: bold; width: 100%;
        text-shadow: 1px 1px 2px #000 !important; font-size: 18px;
        box-shadow: 0 6px 15px rgba(139, 92, 246, 0.5);
        margin-top: 0 !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #6d28d9 0%, #7c3aed 100%);
        box-shadow: 0 6px 25px rgba(139, 92, 246, 0.9);
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
