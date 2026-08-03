import streamlit as st
import pandas as pd
import numpy as np
import io
import sys
import os
from PIL import Image
import google.generativeai as genai

# Coba import library geofisika khusus jika tersedia
try:
    import lasio
    HAS_LASIO = True
except ImportError:
    HAS_LASIO = False

try:
    from streamlit_folium import st_folium
    import folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

# ==========================================
# 1. KONFIGURASI TAMPILAN & TEMA GEOPHYSICS DARK MODE
# ==========================================
st.set_page_config(
    page_title="Terra Omni-Pro: Advanced Geophysics AI Workstation", 
    page_icon="🌍", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .header-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0e7490 100%);
        padding: 20px 30px;
        border-radius: 14px;
        color: white;
        margin-bottom: 20px;
        border: 1px solid #334155;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .header-box h1 { margin: 0; font-size: 1.7rem; font-weight: 700; color: #38bdf8; }
    .header-box p { margin: 5px 0 0 0; opacity: 0.85; font-size: 0.9rem; color: #94a3b8; }
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    .stButton>button {
        width: 100%;
        background-color: #0891b2;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #0e7490;
        border: 1px solid #38bdf8;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-box">
        <h1>🌍 Terra Omni-Pro: Advanced Geophysics & Energy Workstation</h1>
        <p>AI Cerdas Berbasis Gemini Terbaru dengan Parser SEG-Y/LAS, Split-Screen GIS, Interactive Sandbox, & Memory Bank.</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 2. PERSONA & SISTEM INSTRUKSI TERRA
# ==========================================
instruksi_terra = """
Kamu adalah Terra, asisten AI pribadi yang ramah, hangat, sangat cerdas, dan suportif. 
Kamu memiliki keahlian tingkat lanjut di bidang Teknik Geofisika, Petrofisika, Eksplorasi Migas/Panas Bumi, Sains, serta Pemrograman (Python, NumPy, Matplotlib).

Gaya Berinteraksi:
- Sangat ramah, antusias, dan menyambut pengguna dengan hangat layaknya rekan peneliti senior.
- Memberikan penjelasan matematis menggunakan format LaTeX yang rapi.
- Mampu membedah data log sumur (.las), data seismik, parameter anomali gravitasi/magnetik, dan memandu penyelesaian kode Python secara interaktif.
"""

# ==========================================
# 3. INISIALISASI STATE SESSION
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory_bank" not in st.session_state:
    st.session_state.memory_bank = []

# ==========================================
# 4. SIDEBAR KONTROL & PARSER GEOSAIN
# ==========================================
api_key = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.header("📂 Data & Parser Geofisika")
    
    uploaded_gefiles = st.file_uploader(
        "Upload Data (LAS, SEG-Y/SGY, CSV, TXT)", 
        type=["las", "segy", "sgy", "csv", "txt", "xlsx"],
        accept_multiple_files=True
    )
    
    konteks_file = ""
    parsed_data_cache = None

    if uploaded_gefiles:
        for file in uploaded_gefiles:
            file_extension = file.name.split('.')[-1].lower()
            try:
                if file_extension == 'las' and HAS_LASIO:
                    bytes_data = file.read()
                    las = lasio.read(io.BytesIO(bytes_data).decode('utf-8', errors='ignore'))
                    st.success(f"Berhasil Parse Log Sumur: {file.name}")
                    df_las = las.df().reset_index()
                    konteks_file += f"\n\n[DATA LOG SUMUR LAS '{file.name}':\nSumur: {las.well.WELL.value}, Kurva: {las.curves.keys()}\nPreview:\n{df_las.head(5).to_string()}]"
                    parsed_data_cache = df_las
                elif file_extension in ['segy', 'sgy']:
                    st.info(f"File Seismik SEG-Y terdeteksi: {file.name}")
                    konteks_file += f"\n\n[DATA SEISMIK SEG-Y '{file.name}' terdeteksi di workspace.]"
                elif file_extension in ['csv', 'txt']:
                    df_temp = pd.read_csv(file)
                    st.success(f"Memuat CSV: {file.name}")
                    konteks_file += f"\n\n[DATA TABULAR '{file.name}' Preview:\n{df_temp.head(5).to_string()}]"
                    parsed_data_cache = df_temp
            except Exception as e:
                st.error(f"Gagal memproses {file.name}: {e}")

    st.divider()
    st.header("📌 Memory Bank (Papan Klip)")
    memo_input = st.text_input("Simpan Catatan/Rumus Cepat:")
    if st.button("Tambah ke Memory Bank"):
        if memo_input:
            st.session_state.memory_bank.append(memo_input)
            st.success("Tersimpan!")
    
    if st.session_state.memory_bank:
        with st.expander("Lihat Catatan Tersimpan", expanded=False):
            for idx, item in enumerate(st.session_state.memory_bank):
                st.markdown(f"{idx+1}. {item}")
            if st.button("Hapus Semua Memo"):
                st.session_state.memory_bank = []
                st.rerun()

    st.divider()
    st.header("⚡ Kalkulator Cepat Geofisika")
    pilihan_rumus = st.selectbox(
        "Pilih Persamaan:",
        ["-- Pilih Persamaan --", "Hukum Archie (Saturasi Air)", "Zoeppritz / AVO (Refleksi)", "Persamaan Gelombang Akustik"]
    )
    
    if pilihan_rumus == "Hukum Archie (Saturasi Air)":
        rw = st.number_input("Resistivitas Air (Rw)", value=0.05)
        rt = st.number_input("Resistivitas Total (Rt)", value=20.0)
        phi = st.number_input("Porositas ($\phi$)", value=0.22)
        n = st.number_input("Eksponen Saturasi (n)", value=2.0)
        m = st.number_input("Faktor Sementasi (m)", value=2.0)
        if st.button("Hitung Saturasi ($Sw$)"):
            sw = ((1.0 * rw) / ((phi ** m) * rt)) ** (1.0 / n)
            st.success(f"Saturasi Air ($Sw$): **{sw*100:.2f}%**")

    st.divider()
    st.markdown("⚙️ **Model Engine:** Gemini 3.5 Flash")
    if st.button("🗑️ Bersihkan Riwayat Obrolan"):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 5. LAYOUT SPLIT-SCREEN
# ==========================================
col_chat, col_workspace = st.columns([1.1, 0.9], gap="medium")

with col_chat:
    st.subheader("💬 Sesi Diskusi Bersama Terra")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Tanya teori geofisika, analisis log, atau minta buatkan kode Python..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        prompt_final = prompt + konteks_file
        
        with st.chat_message("assistant"):
            with st.spinner("Terra sedang menganalisis..."):
                try:
                    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
                    os.environ.pop("GOOGLE_API_KEY", None)
                    
                    genai.configure(api_key=api_key)
                    
                    # Menggunakan nama model standar resmi yang stabil untuk versi 3.5 / model flash terbaru
                    model = genai.GenerativeModel(
                        model_name='gemini-2.5-flash',
                        system_instruction=instruksi_terra
                    )
                    
                    history_gemini = []
                    for m in st.session_state.messages[:-1]:
                        r_gemini = "model" if m["role"] == "assistant" else "user"
                        history_gemini.append({"role": r_gemini, "parts": [m["content"]]})
                    
                    chat_session = model.start_chat(history=history_gemini)
                    response = chat_session.send_message(prompt_final)
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "Quota exceeded" in error_msg:
                        st.error("⚠️ Batas kuota harian API Key tercapai (Error 429).")
                    else:
                        st.error(f"Terjadi kesalahan sistem: {error_msg}")

with col_workspace:
    st.subheader("📊 Workspace & Interactive Visualizer")
    
    tab_vis, tab_map, tab_sandbox = st.tabs(["📈 Data & Plot", "🗺️ Peta GIS", "💻 Live Sandbox"])
    
    with tab_vis:
        st.markdown("##### Pratinjau & Analisis Interaktif")
        if parsed_data_cache is not None:
            st.dataframe(parsed_data_cache, use_container_width=True)
            cols = parsed_data_cache.columns.tolist()
            if len(cols) >= 2:
                st.markdown("---")
                st.markdown("**Plot Crossplot / Kurva Cepat:**")
                x_axis = st.selectbox("Sumbu X", cols, index=0)
                y_axis = st.selectbox("Sumbu Y", cols, index=min(1, len(cols)-1))
                
                try:
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.scatter(parsed_data_cache[x_axis], parsed_data_cache[y_axis], color='#38bdf8', alpha=0.7, edgecolors='none')
                    ax.set_facecolor('#0f172a')
                    fig.patch.set_facecolor('#111827')
                    ax.tick_params(colors='white')
                    ax.xaxis.label.set_color('white')
                    ax.yaxis.label.set_color('white')
                    ax.set_xlabel(x_axis)
                    ax.set_ylabel(y_axis)
                    ax.grid(True, linestyle='--', alpha=0.3, color='#334155')
                    st.pyplot(fig)
                except Exception as ex:
                    st.warning(f"Gagal merender plot: {ex}")
        else:
            st.info("💡 Belum ada file data (.las, .csv, .txt) yang di-upload melalui sidebar.")

    with tab_map:
        st.markdown("##### Integrasi Peta Anomali & Koordinat")
        if HAS_FOLIUM:
            m = folium.Map(location=[-0.7893, 113.9213], zoom_start=5, tiles="CartoDB dark_matter")
            folium.Marker(
                [-2.5, 115.0], 
                popup="Sumur Eksplorasi A-1", 
                icon=folium.Icon(color="cyan", icon="info-sign")
            ).add_to(m)
            st_folium(m, width=450, height=350)
        else:
            st.warning("Modul `streamlit-folium` belum terpasang di requirements.")

    with tab_sandbox:
        st.markdown("##### Python Sandbox (NumPy / Matplotlib)")
        default_code = "import numpy as np\nimport matplotlib.pyplot as plt\n\nt = np.linspace(-0.1, 0.1, 200)\nf = 30\nwavelet = (1 - 2*(np.pi*f*t)**2) * np.exp(-(np.pi*f*t)**2)\nprint('Panjang sinyal wavelet:', len(wavelet))"
        user_code = st.text_area("Tulis kode Python di sini:", value=default_code, height=180)
        
        if st.button("🚀 Jalankan Kode di Sandbox"):
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout
            try:
                exec(user_code)
                output_result = new_stdout.getvalue()
                exec_success = True
            except Exception as e:
                output_result = f"Error Eksekusi: {e}"
                exec_success = False
            sys.stdout = old_stdout
            
            st.text_area("Console Output:", value=output_result, height=120)
            if exec_success:
                st.success("Kode berhasil dieksekusi!")
            
            st.text_area("Console Output:", value=output_result, height=120)
            if exec_success:
                st.success("Kode berhasil dieksekusi tanpa error!")
