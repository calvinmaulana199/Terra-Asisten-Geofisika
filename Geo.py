import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# ==========================================
# 1. KONFIGURASI TAMPILAN & TEMA ENERGI
# ==========================================
st.set_page_config(
    page_title="Terra - Pakar Geofisika & Energi", 
    page_icon="⚡", 
    layout="centered"
)

# Custom CSS bernuansa Dunia Energi Modern (Teal / Emerald & Clean Tech)
st.markdown("""
    <style>
    /* Mengatur latar belakang utama aplikasi */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Styling Header Utama */
    .main-header {
        background: linear-gradient(135deg, #0f766e 0%, #0369a1 100%);
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .main-header h1 {
        font-size: 2rem;
        margin-bottom: 5px;
        font-weight: 700;
    }
    
    .main-header p {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0;
    }

    /* Styling Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        color: #f8fafc;
    }

    /* Tombol Interaktif */
    .stButton>button {
        width: 100%;
        background-color: #0d9488;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0f766e;
        border: none;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Header Visual Modern
st.markdown("""
    <div class="main-header">
        <h1>⚡ Terra: Pakar Geofisika & Energi</h1>
        <p>Partner Cerdas Eksplorasi Bumi, Analisis Data, dan Komputasi Kebumian</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 2. INSTRUKSI SISTEM (PERSONA TERRA)
# ==========================================
instruksi_terra = """
Kamu adalah Terra, sesosok maskot dan asisten ahli Teknik Geofisika serta Energi yang cerdas, komprehensif, sabar, dan ramah. 
Target audiensmu adalah Mahasiswa Teknik Geofisika (dari tingkat pertama hingga tingkat akhir).

KEMAMPUAN UTAMAMU:
1. Teori & Konsep Geofisika & Energi: Menjelaskan prinsip fisika bumi, eksplorasi migas, panas bumi (geothermal), energi terbarukan, seismologi, geolistrik, geomagnet, dan gravitasi secara akurat.
2. Analisis & Interpretasi Data: Membantu mahasiswa membaca tren data, memahami anomali bawah permukaan, dan menyusun kerangka laporan/tugas besar.
3. Pemrograman & Komputasi: Memberikan solusi coding (Python/MATLAB) apabila mahasiswa menanyakan hal teknis pemrograman kebumian.

FORMAT RESPON:
- Selalu berikan penjelasan konsep dasar fisika/bumi/energi terlebih dahulu.
- Gunakan struktur poin atau langkah-langkah yang rapi agar mudah dibaca.
- Jika user mengunggah file data (CSV), lakukan analisis awal terhadap cuplikan data tersebut.
- Selalu gunakan nada bicara yang hangat, suportif, dan edukatif layaknya asisten dosen atau teman diskusi profesional di bidang energi.
"""

# ==========================================
# 3. SIDEBAR & FITUR UPLOAD
# ==========================================
api_key = st.secrets["GEMINI_API_KEY"]

konteks_data = ""

with st.sidebar:
    st.header("📂 Panel Data Energi & Bumi")
    uploaded_file = st.file_uploader("Upload file data CSV Geofisika", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Berhasil membaca: {uploaded_file.name}")
            st.write("Preview Data (5 baris pertama):")
            st.dataframe(df.head())
            
            konteks_data = f"\n\n[INFO UNTUK TERRA: User telah mengunggah file data. Berikut adalah 5 baris pertama dari data tersebut:\n{df.head().to_string()}]"
        except Exception as e:
            st.error("Gagal membaca file. Pastikan formatnya CSV.")
    
    st.divider()
    st.header("⚙️ Sistem Kontrol")
    st.success("✅ Terhubung: Gemini 3.5 Flash")
    st.info("⚡ Mode Tampilan: Clean Tech Energy")
    
    if st.button("Hapus Riwayat Chat"):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 4. MANAJEMEN HISTORY CHAT
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 5. LOGIKA CHATBOT
# ==========================================
if prompt := st.chat_input("Tanya Terra tentang teori energi, geofisika, analisis data, atau coding..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    prompt_ke_ai = prompt + konteks_data

    with st.chat_message("assistant"):
        try:
            os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
            os.environ.pop("GOOGLE_API_KEY", None)
            
            genai.configure(api_key=api_key)
            
            # Menggunakan model Gemini 3.5 Flash yang sangat responsif
            model = genai.GenerativeModel(
                model_name='gemini-3.5-flash',
                system_instruction=instruksi_terra
            )
            
            history_gemini = []
            for m in st.session_state.messages[:-1]:
                role_gemini = "model" if m["role"] == "assistant" else "user"
                history_gemini.append({"role": role_gemini, "parts": [m["content"]]})
                
            chat = model.start_chat(history=history_gemini)
            
            with st.spinner("Terra sedang memproses analisis sektor energi & kebumian..."):
                response = chat.send_message(prompt_ke_ai)
                
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("❌ Terjadi kesalahan pada sistem API.")
            with st.expander("Lihat Detail Error"):
                st.write(str(e))
