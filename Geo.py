import streamlit as st
import pandas as pd
import numpy as np
import io
import sys
import google.generativeai as genai
import os

# ==========================================
# 1. KONFIGURASI TAMPILAN & TEMA MODERN
# ==========================================
st.set_page_config(
    page_title="Terra Omni-Pro - AI Geofisika & Energi", 
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

st.markdown("""
    <div class="header-box">
        <h1>🌍 Terra Omni-Pro: Asisten Cerdas Geofisika & Energi</h1>
        <p>Dilengkapi Sandbox Kode, Analisis Multimodal Gambar, Kalkulator Cepat, dan Mesin Gemini 3.5 Flash.</p>
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
- Jika diberikan gambar teknis (penampang seismik, log sumur, peta anomali) atau data file, berikan analisis mendalam, tajam, dan terstruktur rapi dengan poin-poin yang mudah dipahami.
"""

# ==========================================
# 3. SIDEBAR: FITUR, UPLOAD, & SANDBOX
# ==========================================
api_key = st.secrets["GEMINI_API_KEY"]

konteks_file = ""

with st.sidebar:
    st.header("📂 Panel Data & Multimodal")
    
    # Upload File Data (CSV, Excel, TXT)
    uploaded_files = st.file_uploader(
        "Upload Data Praktikum (CSV/Excel/TXT)", 
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
                
                st.success(f"Memuat: {file.name}")
                konteks_file += f"\n\n[DATA PRAKTIKUM '{file.name}' Preview:\n{df_temp.head(5).to_string()}]\nStatistik:\n{df_temp.describe().to_string()}"
            except Exception as e:
                st.error(f"Gagal membaca {file.name}: {e}")

    # Upload Gambar untuk Analisis Geoscientific Vision
    uploaded_image = st.file_uploader("Upload Gambar Teknik (Seismik/Log/Peta)", type=["png", "jpg", "jpeg"])
    img_pil = None
    if uploaded_image is not None:
        try:
            from PIL import Image
            img_pil = Image.open(uploaded_image)
            st.image(img_pil, caption="Preview Gambar Analisis", use_container_width=True)
            st.success("Gambar siap dianalisis oleh Terra!")
        except Exception as e:
            st.error(f"Gagal memuat gambar: {e}")

    st.divider()
    st.header("⚡ Kalkulator Cepat Geofisika")
    pilihan_rumus = st.selectbox(
        "Pilih Rumus Praktikum:",
        ["-- Pilih Rumus --", "Hukum Ohm (Geolistrik)", "Densitas Anomali (Gravitasi)", "Kecepatan Gelombang (Seismik)"]
    )
    
    if pilihan_rumus == "Hukum Ohm (Geolistrik)":
        k_val = st.number_input("Faktor Geometri (k)", value=10.0)
        v_val = st.number_input("Voltase (V)", value=5.0)
        i_val = st.number_input("Arus (I)", value=0.5)
        if st.button("Hitung Resistivitas"):
            rho = k_val * (v_val / i_val) if i_val > 0 else 0
            st.success(f"Resistivitas Semu: **{rho:.2f} Ωm**")
            
    elif pilihan_rumus == "Densitas Anomali (Gravitasi)":
        rho2 = st.number_input("Densitas Target ($\rho_2$)", value=2.65)
        rho1 = st.number_input("Densitas Sekitar ($\rho_1$)", value=2.20)
        if st.button("Hitung Kontras"):
            st.success(f"Kontras Densitas: **{rho2 - rho1:.2f} g/cm³**")

    elif pilihan_rumus == "Kecepatan Gelombang (Seismik)":
        jarak = st.number_input("Jarak / Offset (m)", value=50.0)
        waktu = st.number_input("Waktu Travel (s)", value=0.02)
        if st.button("Hitung Kecepatan"):
            v = jarak / waktu if waktu > 0 else 0
            st.success(f"Kecepatan Seismik: **{v:.2f} m/s**")

    st.divider()
    st.header("💻 Live Code Sandbox")
    with st.expander("Buka Python Sandbox"):
        user_code = st.text_area("Tulis kode Python (NumPy/Matplotlib):", "import numpy as np\nprint('Tes NumPy:', np.array([1, 2, 3]))")
        if st.button("Jalankan Kode"):
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout
            try:
                exec(user_code)
                output_result = new_stdout.getvalue()
            except Exception as e:
                output_result = f"Error: {e}"
            sys.stdout = old_stdout
            st.text_area("Output Eksekusi:", value=output_result, height=100)

    st.divider()
    st.header("⚙️ Sistem & Kontrol")
    st.success("✅ Gemini 3.5 Flash Aktif")
    if st.button("🗑️ Bersihkan Riwayat Chat"):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 4. MANAJEMEN RIWAYAT OBROLAN
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 5. LOGIKA UTAMA CHATBOT (GEMINI 3.5 FLASH)
# ==========================================
if prompt := st.chat_input("Tanya apa saja pada Terra (teori, analisis gambar, coding, atau diskusi umum)..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if img_pil:
            st.image(img_pil, width=200, caption="Gambar terlampir")

    # Siapkan konten kiriman ke AI
    prompt_final = prompt + konteks_file
    contents_to_send = [prompt_final]
    if img_pil:
        contents_to_send.append(img_pil)

    with st.chat_message("assistant"):
        with st.spinner("Terra sedang memproses dengan Gemini 3.5..."):
            try:
                os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
                os.environ.pop("GOOGLE_API_KEY", None)
                
                genai.configure(api_key=api_key)
                
                # Menggunakan model Gemini 3.5 Flash
                model = genai.GenerativeModel(
                    model_name='gemini-3.5-flash',
                    system_instruction=instruksi_terra
                )
                
                history_gemini = []
                for m in st.session_state.messages[:-1]:
                    r_gemini = "model" if m["role"] == "assistant" else "user"
                    history_gemini.append({"role": r_gemini, "parts": [m["content"]]})
                
                chat_session = model.start_chat(history=history_gemini)
                response = chat_session.send_message(contents_to_send)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error("❌ Terjadi kesalahan pada sistem AI.")
                with st.expander("Detail Error"):
                    st.write(str(e))
