import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
import os

# ==========================================
# 1. KONFIGURASI TAMPILAN & TEMA MODERN
# ==========================================
st.set_page_config(
    page_title="Terra Ultimate - AI Geofisika & Energi", 
    page_icon="🌍", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    .header-box {
        background: linear-gradient(135deg, #0f766e 0%, #0284c7 100%);
        padding: 20px 30px;
        border-radius: 14px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .header-box h1 { margin: 0; font-size: 1.8rem; font-weight: 700; }
    .header-box p { margin: 5px 0 0 0; opacity: 0.9; font-size: 0.95rem; }
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    .stButton>button {
        width: 100%;
        background-color: #0d9488;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0f766e;
    }
    </style>
""", unsafe_allow_html=True)

# Header Utama
st.markdown("""
    <div class="header-box">
        <h1>🌍 Terra Ultimate: Asisten Cerdas Geofisika & Energi</h1>
        <p>Solusi komprehensif teori bumi, analisis data praktikum, kalkulator cepat, dan pemrograman berbasis Gemini 3.5.</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 2. INSTRUKSI SISTEM (PERSONA TERRA)
# ==========================================
instruksi_terra = """
Kamu adalah Terra, asisten AI pribadi yang ramah, hangat, sangat cerdas, dan suportif (mirip seperti karakter Gemini). 
Kamu memiliki keahlian mendalam di bidang Teknik Geofisika, Energi, Sains, serta Pemrograman (Python, Numpy, Matplotlib, MATLAB).

Gaya Berinteraksi:
- Sangat ramah, antusias, dan menyambut siapa saja dengan hangat.
- Fleksibel: Sanggup menjawab pertanyaan akademik geofisika, analisis data praktikum, coding, hingga pertanyaan umum layaknya asisten AI serba bisa.
- Jika diberikan data atau file, berikan analisis yang tajam, terstruktur rapi dengan poin-poin yang mudah dipahami.
"""

# ==========================================
# 3. SIDEBAR: FITUR LENGKAP & KALKULATOR CEPAT
# ==========================================
api_key = st.secrets["GEMINI_API_KEY"]

konteks_file = ""

with st.sidebar:
    st.header("📂 Panel Data & Praktikum")
    uploaded_files = st.file_uploader(
        "Upload file data praktikum (CSV, Excel, TXT)", 
        type=["csv", "xlsx", "txt"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for file in uploaded_files:
            try:
                if file.name.endswith('.csv') or file.name.endswith('.txt'):
                    df_temp = pd.read_csv(file)
                else:
                    df_temp = pd.read_excel(file)
                
                st.success(f"Berhasil memuat: {file.name}")
                with st.expander(f"Preview: {file.name}"):
                    st.dataframe(df_temp.head(3))
                
                konteks_file += f"\n\n[DATA PRAKTIKUM '{file.name}' Preview:\n{df_temp.head(5).to_string()}]\nStatistik Ringkas:\n{df_temp.describe().to_string()}"
            except Exception as e:
                st.error(f"Gagal membaca {file.name}: {e}")

    st.divider()
    st.header("⚡ Kalkulator Cepat Geofisika")
    pilihan_rumus = st.selectbox(
        "Pilih Rumus Praktikum:",
        ["-- Pilih Rumus --", "Hukum Ohm (Geolistrik)", "Densitas Anomali (Gravitasi)", "Kecepatan Gelombang (Seismik)"]
    )
    
    if pilihan_rumus == "Hukum Ohm (Geolistrik)":
        st.caption("Menghitung Resistivitas Semu ($\rho$ = k * V / I)")
        k_val = st.number_input("Faktor Geometri (k)", value=10.0)
        v_val = st.number_input("Voltase (V)", value=5.0)
        i_val = st.number_input("Arus (I)", value=0.5)
        if st.button("Hitung Resistivitas"):
            if i_val > 0:
                rho = k_val * (v_val / i_val)
                st.success(f"Hasil Resistivitas Semu: **{rho:.2f} Ωm**")
            else:
                st.error("Arus (I) tidak boleh 0!")
                
    elif pilihan_rumus == "Densitas Anomali (Gravitasi)":
        st.caption("Kontras Densitas ($\Delta\rho = \rho_2 - \rho_1$)")
        rho2 = st.number_input("Densitas Target ($\rho_2$)", value=2.65)
        rho1 = st.number_input("Densitas Sekitar ($\rho_1$)", value=2.20)
        if st.button("Hitung Kontras"):
            kontras = rho2 - rho1
            st.success(f"Kontras Densitas: **{kontras:.2f} g/cm³**")

    elif pilihan_rumus == "Kecepatan Gelombang (Seismik)":
        st.caption("Kecepatan Gelombang ($v = s / t$)" )
        jarak = st.number_input("Jarak Geofon / Offset (m)", value=50.0)
        waktu = st.number_input("Waktu Travel (s)", value=0.02)
        if st.button("Hitung Kecepatan"):
            if waktu > 0:
                v = jarak / waktu
                st.success(f"Kecepatan Seismik: **{v:.2f} m/s**")
            else:
                st.error("Waktu tidak boleh 0!")

    st.divider()
    st.header("⚙️ Sistem & Kontrol")
    st.success("✅ Gemini 3.5 Flash Aktif")
    if st.button("🗑️ Bersihkan Riwayat Chat"):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 4. MANAJEMEN RIWAYAT OBROLAN (CLEAN & NEAT)
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan seluruh riwayat obrolan secara rapi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 5. LOGIKA UTAMA CHATBOT (GEMINI 3.5)
# ==========================================
if prompt := st.chat_input("Tanya apa saja pada Terra (teori, coding numpy/matplotlib, atau diskusi umum)..."):
    
    # Simpan dan tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gabungkan prompt dengan cuplikan data file jika ada
    prompt_final = prompt + konteks_file

    with st.chat_message("assistant"):
        with st.spinner("Terra sedang merespon dengan cerdas..."):
            try:
                os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
                os.environ.pop("GOOGLE_API_KEY", None)
                
                genai.configure(api_key=api_key)
                
                # Menggunakan model Gemini 3.5 Flash terbaru
                model = genai.GenerativeModel(
                    model_name='gemini-3.5-flash',
                    system_instruction=instruksi_terra
                )
                
                # Membangun riwayat percakapan untuk konteks multi-turn
                history_gemini = []
                for m in st.session_state.messages[:-1]:
                    r_gemini = "model" if m["role"] == "assistant" else "user"
                    history_gemini.append({"role": r_gemini, "parts": [m["content"]]})
                
                chat_session = model.start_chat(history=history_gemini)
                response = chat_session.send_message(prompt_final)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error("❌ Terjadi kesalahan pada sistem AI.")
                with st.expander("Detail Error"):
                    st.write(str(e))
