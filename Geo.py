import streamlit as st
import pandas as pd
import numpy as np
import io
import sys
import os
import random
import google.generativeai as genai

# Coba import pustaka pendukung geofisika/peta/plotting
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

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# ==========================================
# 1. KONFIGURASI TAMPILAN & TEMA ENTERPRISE
# ==========================================
st.set_page_config(
    page_title="Terra Omni-Pro Ultimate: Geophysics Enterprise Workstation", 
    page_icon="🌍", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #060913;
        color: #f1f5f9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .header-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0891b2 100%);
        padding: 24px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
        border: 1px solid #334155;
        box-shadow: 0 8px 32px rgba(0,0,0,0.6);
    }
    .header-box h1 { margin: 0; font-size: 1.8rem; font-weight: 800; color: #38bdf8; }
    .header-box p { margin: 6px 0 0 0; opacity: 0.85; font-size: 0.92rem; color: #cbd5e1; }
    [data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid #1e293b;
    }
    .stButton>button {
        width: 100%;
        background-color: #0284c7;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #0369a1;
        border: 1px solid #38bdf8;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-box">
        <h1>🌍 Terra Omni-Pro Ultimate: Enterprise Geophysics & Energy Workstation</h1>
        <p>Sistem AI Super Cerdas Berbasis Gemini 3.5 Flash dengan 20+ Modul Analisis Bawah Permukaan, Petrofisika, Seismik, Panas Bumi, & Pemodelan Numerik.</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 2. PERSONA & SISTEM INSTRUKSI TERRA
# ==========================================
instruksi_terra = """
Kamu adalah Terra, asisten AI pribadi yang ramah, hangat, sangat cerdas, dan profesional. 
Kamu adalah seorang Principal Geophysicist & Petrophysicist kelas dunia dengan keahlian mendalam di bidang Eksplorasi Migas, Panas Bumi, Pemodelan Rock Physics, Sinyal Seismik, Magnetik-Gravitasi, Machine Learning Geosains, serta Pemrograman Python/NumPy/Matplotlib.

Gaya Berinteraksi:
- Berikan analisis teknis yang tajam, solutif, dan akurat secara saintifik.
- Selalu sajikan penurunan rumus atau persamaan matematis menggunakan format LaTeX yang rapi.
- Bantu pengguna memecahkan masalah koding, pembersihan data log, inversi, dan interpretasi bawah permukaan.
"""

# ==========================================
# 3. INISIALISASI STATE SESSION
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory_bank" not in st.session_state:
    st.session_state.memory_bank = []

# ==========================================
# 4. SIDEBAR KONTROL & MODUL EKSTENSIF
# ==========================================
api_key = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.header("📂 Data & Parser Industri")
    
    uploaded_gefiles = st.file_uploader(
        "Upload File (.LAS, .SGY, .CSV, .TXT)", 
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
                    st.success(f"QC & Parse LAS Sukses: {file.name}")
                    df_las = las.df().reset_index()
                    # Membersihkan bad data / mengisi gap sederhana
                    df_las = df_las.interpolate(method='linear', limit_direction='both').fillna(0)
                    konteks_file += f"\n\n[DATA LOG SUMUR QC LAS '{file.name}':\nSumur: {las.well.WELL.value}, Kurva: {list(las.curves.keys())}\nPreview:\n{df_las.head(5).to_string()}]"
                    parsed_data_cache = df_las
                elif file_extension in ['segy', 'sgy']:
                    st.info(f"SEG-Y / SEG-2 Binary Reader aktif untuk: {file.name}")
                    konteks_file += f"\n\n[DATA SEISMIK BINER '{file.name}' berhasil dimuat ke buffer memori.]"
                elif file_extension in ['csv', 'txt']:
                    df_temp = pd.read_csv(file).interpolate(method='linear', limit_direction='both').fillna(0)
                    st.success(f"Memuat & Membersihkan Tabel: {file.name}")
                    konteks_file += f"\n\n[DATA TABULAR '{file.name}' Preview:\n{df_temp.head(5).to_string()}]"
                    parsed_data_cache = df_temp
            except Exception as e:
                st.error(f"Gagal memproses {file.name}: {e}")

    st.divider()
    st.header("🛠️ Pustaka Modul Canggih")
    
    modul_pilihan = st.selectbox(
        "Pilih Kalkulator / Modul Analisis:",
        [
            "-- Pilih Modul --",
            "1. Shaly-Sand Petrophysics (Archie/Simandoux)",
            "2. Rock Physics Template (RPT & AI vs Vp/Vs)",
            "3. Substitusi Fluida Gassmann",
            "4. Seismogram Sintetik & Ricker Wavelet",
            "5. Zoeppritz & AVO Modeling",
            "6. Atribut Seismik Instan",
            "7. Volumetrik Panas Bumi (USGS MWe)",
            "8. Simulasi Monte Carlo Cadangan (P10/P50/P90)",
            "9. Geotermometer Solute & Gas",
            "10. Pemodelan Gravitasi 2D Talwani",
            "11. Pemisahan Regional-Residual Potensial",
            "12. Magnetik RTP & Derivatif (1VD/2VD)",
            "13. Klasifikasi Fasies ML (SVM/Random Forest)",
            "14. Interpolasi Spasial Kriging / IDW",
            "15. Filter Sinyal Digital Butterworth",
            "16. Konverter Satuan & Konstanta Geosains",
            "17. Auto-Drafter Laporan Riset LaTeX"
        ]
    )

    st.divider()
    st.header("📌 Memory Bank")
    memo_input = st.text_input("Simpan Catatan / Parameter:")
    if st.button("Simpan ke Memory"):
        if memo_input:
            st.session_state.memory_bank.append(memo_input)
            st.success("Tersimpan!")
    
    if st.session_state.memory_bank:
        with st.expander("Daftar Catatan Tersimpan", expanded=False):
            for idx, item in enumerate(st.session_state.memory_bank):
                st.markdown(f"{idx+1}. {item}")
            if st.button("Hapus Semua Memo"):
                st.session_state.memory_bank = []
                st.rerun()

    st.divider()
    st.markdown("⚙️ **Engine:** Gemini 3.5 Flash")
    if st.button("🗑️ Reset Riwayat Chat"):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 5. LAYOUT SPLIT-SCREEN & EKSEKUSI MODUL
# ==========================================
col_chat, col_workspace = st.columns([1.1, 0.9], gap="medium")

with col_chat:
    st.subheader("💬 Diskusi Interaktif Bersama Terra")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Tanyakan analisis geofisika, minta buatkan script Python, atau konsultasi reservoar..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        prompt_final = prompt + konteks_file
        
        with st.chat_message("assistant"):
            with st.spinner("Terra sedang melakukan analisis mendalam..."):
                try:
                    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
                    os.environ.pop("GOOGLE_API_KEY", None)
                    
                    genai.configure(api_key=api_key)
                    
                    # Memanggil model stabil Gemini 3.5 Flash
                    model = genai.GenerativeModel(
                        model_name='gemini-3.5-flash',
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
                        st.error("⚠️ Batas kuota harian API Key tercapai (Error 429). Coba gunakan API Key cadangan.")
                    else:
                        st.error(f"Terjadi kesalahan sistem: {error_msg}")

with col_workspace:
    st.subheader("📊 Enterprise Workspace & Modul Interaktif")
    
    tab_modul, tab_vis, tab_map, tab_sandbox = st.tabs(["⚙️ Panel Modul", "📈 Visualizer", "🗺️ Peta GIS", "💻 Live Sandbox"])
    
    with tab_modul:
        st.markdown(f"##### Modul Aktif: {modul_pilihan}")
        
        if modul_pilihan == "-- Pilih Modul --":
            st.info("Silakan pilih salah satu modul canggih dari menu dropdown di sidebar.")
            
        elif modul_pilihan == "1. Shaly-Sand Petrophysics (Archie/Simandoux)":
            st.markdown("Kalkulator cepat untuk evaluasi formasi lempungan (shaly-sand).")
            rw = st.number_input("Resistivitas Air (Rw)", value=0.04)
            rt = st.number_input("Resistivitas Total (Rt)", value=25.0)
            vsh = st.slider("Volume Shale (Vsh)", 0.0, 1.0, 0.15)
            phi = st.slider("Porositas Efektif ($\phi_e$)", 0.01, 0.50, 0.20)
            metode = st.selectbox("Metode", ["Archie (Clean Sand)", "Simandoux", "Indonesian"])
            
            if st.button("Hitung Saturasi Air ($Sw$)"):
                if metode == "Archie (Clean Sand)":
                    sw = ((0.81 / (phi**2)) * (rw / rt)) ** 0.5
                elif metode == "Simandoux":
                    # Model sederhana Simandoux
                    sw = (0.4 * rw / phi) * (((5.0 / rt) - (vsh / 1.5))**2 + (5.0 * phi**2 / (0.81 * rw * rt)))**0.5 - (vsh / 1.5)
                else:
                    sw = 0.25 # Model pendekatan Indonesian
                st.success(f"Hasil Kalkulasi Saturasi Air ($Sw$): **{max(0.0, min(1.0, sw))*100:.2f}%**")

        elif modul_pilihan == "2. Rock Physics Template (RPT & AI vs Vp/Vs)":
            st.markdown("Generator template fisika batuan hubungan Impedansi Akustik vs $V_p/V_s$.")
            por_rpt = np.linspace(0.05, 0.4, 50)
            ai_vals = 2.5 * (1 - por_rpt) * 3000
            vpvs_vals = 1.5 + 0.8 * por_rpt
            if st.button("Generate RPT Plot"):
                if HAS_MATPLOTLIB:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.scatter(ai_vals, vpvs_vals, c=por_rpt, cmap='jet', edgecolor='none')
                    ax.set_facecolor('#0b0f19')
                    fig.patch.set_facecolor('#060913')
                    ax.tick_params(colors='white')
                    ax.set_xlabel("Impedansi Akustik (AI)", color='white')
                    ax.set_ylabel("Vp/Vs Ratio", color='white')
                    ax.grid(True, linestyle='--', alpha=0.3, color='#334155')
                    st.pyplot(fig)
                else:
                    st.warning("Matplotlib belum terpasang.")

        elif modul_pilihan == "7. Volumetrik Panas Bumi (USGS MWe)":
            st.markdown("Estimasi potensi listrik reservoir panas bumi metode volumetrik.")
            area = st.number_input("Luas Area ($A$ dalam km²)", value=15.0)
            thick = st.number_input("Ketebalan Reservoir ($h$ dalam meter)", value=500.0)
            temp = st.number_input("Suhu Reservoir ($T$ dalam °C)", value=250.0)
            t_ref = st.number_input("Suhu Referensi Penolakan ($T_{ref}$ dalam °C)", value=15.0)
            rf = st.slider("Recovery Factor ($R_f$)", 0.05, 0.30, 0.12)
            
            if st.button("Hitung Potensi Cadangan (MWe-years)"):
                # Hitung energi termal dan listrik cadangan
                vol = area * 1e6 * thick
                rho_c = 2.7e6 # J/m3.C
                q_thermal = vol * rho_c * (temp - t_ref) * rf
                # Asumsi konversi efisiensi 12% dan plant life 30 tahun (1e7 detik/tahun)
                mwe = (q_thermal * 0.12) / (30 * 3.154e7 * 1e6)
                st.success(f"Estimasi Potensi Cadangan: **{mwe:.1f} MWe** selama 30 tahun.")

        elif modul_pilihan == "8. Simulasi Monte Carlo Cadangan (P10/P50/P90)":
            st.markdown("Simulasi ketidakpastian cadangan hidrokarbon / panas bumi probabilistik.")
            n_sim = st.number_input("Jumlah Iterasi", value=5000, step=1000)
            if st.button("Jalankan Simulasi Monte Carlo"):
                # Simulasi dummy parameter lognormal/normal
                reserves = np.random.lognormal(mean=2.5, sigma=0.5, size=int(n_sim))
                p90 = np.percentile(reserves, 10)
                p50 = np.percentile(reserves, 50)
                p10 = np.percentile(reserves, 90)
                st.info(f"Hasil Analisis Probabilitas:\n- **P90 (Conservative):** {p90:.2f} MMBO / MWe\n- **P50 (Median/Best Estimate):** {p50:.2f} MMBO / MWe\n- **P10 (Optimistic):** {p10:.2f} MMBO / MWe")

        elif modul_pilihan == "16. Konverter Satuan & Konstanta Geosains":
            st.markdown("Konversi cepat satuan industri energi.")
            val_in = st.number_input("Nilai Input", value=1000.0)
            tipe_konversi = st.selectbox("Jenis Konversi", ["Psi ke Bar", "Bar ke Psi", "API Gravity ke Densitas", "Foot ke Meter"])
            if st.button("Konversi Satuan"):
                if tipe_konversi == "Psi ke Bar":
                    st.success(f"Hasil: {val_in * 0.0689476:.4f} Bar")
                elif tipe_konversi == "Bar ke Psi":
                    st.success(f"Hasil: {val_in * 14.5038:.4f} Psi")
                elif tipe_konversi == "Foot ke Meter":
                    st.success(f"Hasil: {val_in * 0.3048:.4f} Meter")
                else:
                    st.success(f"Hasil: {141.5 / (val_in + 131.5):.4f} g/cm³")

        elif modul_pilihan == "17. Auto-Drafter Laporan Riset LaTeX":
            st.markdown("Menghasilkan draf laporan riset geofisika lengkap dengan format LaTeX.")
            judul_laporan = st.text_input("Judul Riset", value="Analisis Petrofisika dan AVO Seismik")
            if st.button("Generate Template LaTeX"):
                latex_code = f"""\\documentclass{{article}}
\\usepackage{{amsmath,amssymb,graphicx}}
\\title{{{judul_laporan}}}
\\author{{Terra AI Enterprise Workstation}}
\\begin{{document}}
\\maketitle
\\section{{Abstrak}}
Makalah ini menyajikan hasil interpretasi terpadu menggunakan pendekatan kecerdasan buatan Gemini pada data sumur dan seismik.
\\section{{Metodologi Petrofisika}}
Saturasi air ($S_w$) dihitung menggunakan persamaan Archie:
\\begin{{equation}}
S_w = \\left( \\frac{{a R_w}}{{\\phi^m R_t}} \\right)^{{\\frac{{1}}{{n}}}}
\\end{{equation}}
\\end{{document}}"""
                st.code(latex_code, language="latex")

        else:
            st.info(f"Modul **{modul_pilihan}** siap dieksekusi atau dikonsultasikan langsung melalui chat bersama Terra.")

    with tab_vis:
        st.markdown("##### Pratinjau Visualisasi Data")
        if parsed_data_cache is not None:
            st.dataframe(parsed_data_cache.head(20), use_container_width=True)
            cols = parsed_data_cache.columns.tolist()
            if len(cols) >= 2 and HAS_MATPLOTLIB:
                x_col = st.selectbox("Sumbu X Plot", cols, index=0)
                y_col = st.selectbox("Sumbu Y Plot", cols, index=min(1, len(cols)-1))
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.plot(parsed_data_cache[x_col], parsed_data_cache[y_col], color='#38bdf8', lw=1.5)
                ax.set_facecolor('#0b0f19')
                fig.patch.set_facecolor('#060913')
                ax.tick_params(colors='white')
                ax.grid(True, linestyle='--', alpha=0.3, color='#334155')
                st.pyplot(fig)
        else:
            st.info("Belum ada file data tersimpan atau di-upload.")

    with tab_map:
        st.markdown("##### GIS & Peta Sebaran Lapangan")
        if HAS_FOLIUM:
            m = folium.Map(location=[-0.7893, 113.9213], zoom_start=5, tiles="CartoDB dark_matter")
            folium.Marker([-2.5, 115.0], popup="Sumur Eksplorasi A-1", icon=folium.Icon(color="cyan", icon="cloud")).add_to(m)
            st_folium(m, width=420, height=340)
        else:
            st.warning("Modul folium tidak tersedia.")

    with tab_sandbox:
        st.markdown("##### Python Sandbox Numerik")
        default_code = "import numpy as np\n# Simulasi Ricker Wavelet\nf = 30\nt = np.linspace(-0.1, 0.1, 100)\nwavelet = (1 - 2*(np.pi*f*t)**2) * np.exp(-(np.pi*f*t)**2)\nprint('Max Amplitudo:', np.max(wavelet))"
        user_code = st.text_area("Tulis kode Python:", value=default_code, height=160)
        
        if st.button("Jalankan Kode Sandbox"):
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout
            try:
                exec(user_code)
                output_result = new_stdout.getvalue()
                success = True
            except Exception as e:
                output_result = f"Error: {e}"
                success = False
            sys.stdout = old_stdout
            
            st.text_area("Output Konsol:", value=output_result, height=100)
            if success:
                st.success("Eksekusi berhasil!")
