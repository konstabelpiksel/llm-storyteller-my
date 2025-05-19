import streamlit as st
import requests
import json
import re

# Configuración de la página
st.set_page_config(
    page_title="LLM StoryTeller",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
    .main {
        padding: 2rem;
        background-color: transparent;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
        background-color: #FF4B4B;
        color: white !important;
        transition: transform 0.2s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        color: white !important;
        background-color: #FF4B4B;
    }
    .stButton>button:active, .stButton>button:focus {
        color: white !important;
    }
    .story-container {
        background-color: #ffffff;
        padding: 3rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    .story-text {
        color: #2C3E50;
        font-size: 1.2rem;
        line-height: 1;
        font-family: 'Crimson Text', 'Georgia', serif !important;
        text-align: justify;
        white-space: pre-wrap;
        letter-spacing: 0.3px;
        word-spacing: 1px;
        text-rendering: optimizeLegibility;
    }
    .story-text p {
        margin-bottom: 0.5rem;
        font-size: inherit;
        font-family: inherit;
        line-height: inherit;
    }
    .story-text::first-letter {
        font-size: 3.5rem;
        font-weight: bold;
        float: left;
        line-height: 1;
        padding-right: 12px;
        color: #FF4B4B;
    }
    @media (max-width: 768px) {
        .story-container {
            padding: 1.5rem;
        }
        .story-text {
            font-size: 1.1rem;
            line-height: 1.6;
        }
    }
    .input-container {
        padding: 1rem;
        border-radius: 10px;
        margin: 0;
    }
    .custom-input {
        border: 1px solid #ddd !important;
        border-radius: 5px !important;
        padding: 0.5rem !important;
    }
    div.stMarkdown {
        background-color: transparent !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: transparent !important;
    }
    .sidebar .element-container {
        background-color: transparent !important;
    }
    .row-widget {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    .stTextInput > div {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Título y descripción
st.title("🌟 LLM StoryTeller")

st.info("""
**Maklumat proses:**
Setiap proses boleh menggunakan model AI yang berbeza (pilih pada konfigurasi)\n
Proses 1: Jana skrip cerita. \n
Proses 2: Hasilkan penulisan cerita. \n
Proses 3: Baiki tatabahasa dan kejituan cerita. 
""")

# Configuración de los endpoints
BASE_URL = "http://192.168.100.47:1234/v1" #http://192.168.100.47:1234/v1/chat/completions
AVAILABLE_MODELS = {
    "Llama 1B": "llama-3.2-1b-instruct",
    "Qwen 1.5B": "qwen2.5-1.5b-instruct",
    "Gemma 2 9B":"gemma-2-ataraxy-9b", #lemon07r/Gemma-2-Ataraxy-v2-9B
}

def call_llm(prompt, model, temperature=0.7):
    """Fungsi untuk memanggil LLM"""
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            json={
                "model": AVAILABLE_MODELS[model],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": 3200 #2048
            }
        )
        result = response.json()
        if "choices" not in result or not result["choices"]:
            raise Exception("Tiada respons diterima daripada model LLM")
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Ralat sambungan model LLM: {str(e)}")
        return None

def preprocess_story(text):
    """
    Membuang tag markup daripada teks yang dijana dari model LLM
    """
    import re
    # Eliminar símbolos markdown comunes
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)  # Eliminar headers (#, ##, etc)
    text = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', text)  # Eliminar énfasis (* y _)
    text = re.sub(r'`([^`]+)`', r'\1', text)  # Eliminar código inline
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)  # Eliminar bullets
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # Eliminar listas numeradas
    return text.strip()

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    # Selección de modelos para cada paso
    st.subheader("Pemilihan model LLM")
    outline_model = st.selectbox("Model untuk struktur cerita", AVAILABLE_MODELS.keys(), key="outline")
    writing_model = st.selectbox("Model untuk penulisan", AVAILABLE_MODELS.keys(), key="writing")
    review_model = st.selectbox("Model untuk semakan", AVAILABLE_MODELS.keys(), key="review")
    
    # Configuración de temperatura
    st.subheader("Tetapan Respon LLM")
    temperature = st.slider(
        "Temperature (Semakin tinggi = Semakin Kreatif)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Tetapan untuk tahap kreativiti model. Nilai tinggi = kreativiti tinggi, nilai rendah = konsistensi tinggi"
    )
    
    # Idioma
    language = st.text_input("Bahasa log", "Melayu moden Malaysia")

# Formulario principal
col1, col2 = st.columns(2)

with col1:
    main_character = st.text_input("Watak utama", 
                                 placeholder="contoh: Hang Tuah, pahlawan Melayu",
                                 key="main_char")
    location = st.text_input("Tempat/Lokasi", 
                           placeholder="contoh: Bandar Melaka, Istana Melayu Melaka",
                           key="location")
    
with col2:
    secondary_character = st.text_input("Watak kedua",
                                      placeholder="contoh: Hang Jebat, pahlawan Melayu, sahabat Hang Tuah",
                                      key="sec_char")
    key_action = st.text_input("Aksi Utama",
                              placeholder="contoh: pertarungan mempertahankan Kesultanan Melaka",
                              key="action")

# Selección de longitud y estilo
col3, col4 = st.columns(2)

with col3:
    length = st.selectbox(
        "Panjang cerita",
        ["Cerita pendek (250 pp)", 
         "Cerita sederhana (500 pp)",
         "Novel pendek (1000 pp)"]
    )

with col4:
    style = st.selectbox(
        "Genre naratif",
        ["Misteri", "Fiksyen Sains", "Percintaan", "Fantasí", "Komedi", "Seram", "Aksi", "Jenayah"]
    )

# Botón de generación fuera del formulario
generate = st.button("✨ Menjana Cerita")

if generate:
    with st.spinner("🎭 Menjana skrip cerita..."):
        outline_prompt = f"""Hasilkan skrip untuk cerita dalam bahasa {language} dengan unsur-unsur berikut:
        - {main_character} (protagonis/watak utama)
        - {secondary_character} (watak kedua)
        - Terletak di {location}
        - Fokus kepada {key_action}
        - Gaya {style}
        - Panjang cerita {length}

        PENTING: Jawab HANYA dengan rangka cerita. JANGAN ulangi arahan ini atau gunakan bullet point"""

        outline = call_llm(outline_prompt, outline_model, temperature)
        
        if outline:
            with st.spinner("✍️ Menggilap naratif cerita..."):
                writing_prompt = f"""Berikut adalah rangka cerita:

{outline}

Tuliskan cerita berdasarkan garis panduan dibawah dengan terperinci menggunakan laras bahasa yang baik, dengan menekankan:
- Kekalkan gaya {style}
- Tambahkan elemen emosi dan sensori 
- Gunakan dialog percakapan semulajadi
- Panjang cerita (SANGAT PENTING): {length}

PENTING: Jawab HANYA dengan cerita akhir. JANGAN ulangi arahan ini atau gunakan bullet point"""

                story = call_llm(writing_prompt, writing_model, temperature)
                
                if story:
                    with st.spinner("🔍 Memugar dan memperelok penulisan..."):
                        review_prompt = f"""Ini adalah penulisan cerita yang perlu diperbaiki dan dimurnikan:

{story}

Semak, perbaiki dan murnikan cerita ini tetapi pastikan elemen-elemen ini dipelihara:
- gaya cerita {style}
- Betulkan kesalahan tatabahasa dan ejaan
- Murnikan dialog dan penerangan dalam cerita
- Kekalkan panjang cerita! SANGAT PENTING! ({length})

PENTING: Jawab HANYA dengan cerita akhir yang telah diperbaiki dan dimurnikan. JANGAN ulangi arahan ini atau gunakan bullet point"""

                        final_story = call_llm(review_prompt, review_model, temperature)
                        
                        if final_story:
                            st.subheader("📖 Srkip Cerita Akhir")
                            # Preprocesar la historia antes de mostrarla
                            cleaned_story = preprocess_story(final_story)
                            st.markdown(
                                f'<div class="story-container"><div class="story-text">{cleaned_story}</div></div>',
                                unsafe_allow_html=True
                            )
                            
                            # Botón para descargar
                            st.download_button(
                                label="📥 Muatturun Cerita (format TXT)",
                                data=final_story,
                                file_name="cerita.txt",
                                mime="text/plain"
                            )
