import streamlit as st
import requests
import json
import re
#import openai

# page config
st.set_page_config(
    page_title="LLM StoryTeller",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# css
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
st.title("🌟 Tukang Cerita LLM")

st.info("""
**Maklumat proses:**
Setiap proses boleh menggunakan model AI yang berbeza (pilih pada konfigurasi)\n
Proses 1: Jana skrip cerita. \n
Proses 2: Gilap naratif cerita. \n
Proses 3: Memugar penulisan. 
""")

# Chatgpt endpoint configuration
BASE_URL = "https://api.openai.com/v1"
CHATGPT_MODEL = "gpt-4.1"

def call_llm(prompt, model=CHATGPT_MODEL, temperature=0.7, api_key=None):
    """Fungsi untuk memanggil CHATGPT"""
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": 3200
            },
            timeout=30  # Optional: adds a timeout to avoid hanging
        )
        response.raise_for_status()  # Raise error if HTTP error occurred
        result = response.json()
        
        if "choices" not in result or not result["choices"]:
            raise Exception("Tiada respons diterima daripada model LLM")
        return result["choices"][0]["message"]["content"]
    
    except requests.exceptions.RequestException as req_err:
        st.error(f"Ralat rangkaian: {str(req_err)}")
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

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    st.subheader("ChatGPT API Key")
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = ""

    api_key_input = st.text_input("API Key", type="password", value=st.session_state["api_key"])
    if api_key_input and api_key_input != st.session_state["api_key"]:
        st.session_state["api_key"] = api_key_input
    
    st.subheader("Tetapan Respon LLM")
    temperature = st.slider(
        "Temperature (Semakin tinggi = Semakin Kreatif)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Tetapan untuk tahap kreativiti model. Nilai tinggi = kreativiti tinggi, nilai rendah = konsistensi tinggi"
    )
    
    language = st.text_input("Bahasa log", "Melayu moden Malaysia")
    
    if st.button("❌ Padam API Key"):
        st.session_state["api_key"] = ""
        st.experimental_rerun()

# Main form
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

# Length and style selection
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
        ["Misteri", "Fiksyen Sains", "Percintaan", "Fantasí", "Komedi", "Seram", "Aksi", "Jenayah", "Erotik"]
    )

# Buttons and do shit

generate = st.button("✨ Menjana Cerita")


# required_fields = [main_character, location, secondary_character, key_action]
# if not all(required_fields):
#     st.warning("Sila lengkapkan semua medan input untuk menjana cerita.")
    
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

        if not st.session_state["api_key"] or not st.session_state["api_key"].startswith("sk-"):
            st.warning("Masukkan API Key yang sah. Bermula dengan 'sk-'")
        else:
            outline = call_llm(outline_prompt, CHATGPT_MODEL, temperature, st.session_state["api_key"])
        
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

                story = call_llm(writing_prompt, CHATGPT_MODEL, temperature, st.session_state["api_key"])
                
                if story:
                    with st.spinner("🔍 Memugar penulisan..."):
                        review_prompt = f"""Ini adalah penulisan cerita yang perlu diperbaiki dan dimurnikan:

{story}

Semak, perbaiki dan murnikan cerita ini tetapi pastikan elemen-elemen ini dipelihara:
- gaya cerita {style}
- Betulkan kesalahan tatabahasa dan ejaan
- Murnikan dialog dan penerangan dalam cerita
- Kekalkan panjang cerita! SANGAT PENTING! ({length})

PENTING: Jawab HANYA dengan cerita akhir yang telah diperbaiki dan dimurnikan. JANGAN ulangi arahan ini atau gunakan bullet point"""

                        final_story = call_llm(review_prompt, CHATGPT_MODEL, temperature, st.session_state["api_key"])
                        
                        if final_story:
                            st.subheader("📖 Srkip Cerita Akhir")
                            cleaned_story = preprocess_story(final_story)
                            st.markdown(
                                f'<div class="story-container"><div class="story-text">{cleaned_story}</div></div>',
                                unsafe_allow_html=True
                            )
                            
                            st.download_button(
                                label="📥 Muatturun Cerita (format TXT)",
                                data=final_story,
                                file_name="cerita.txt",
                                mime="text/plain"
                            )
