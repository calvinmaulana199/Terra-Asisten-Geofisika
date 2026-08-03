import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# ==========================================
# 1. KONFIGURASI HALAMAN & TEMA TERRA
# ==========================================
st.set_page_config(
    page_title="Terra - Asisten Geofisika & Energi",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS biar tampilan Terra lebih hangat, ramah, dan estetik (Tema Earth-Geophysics)
st.markdown("""
    <style>
    .main {
        background-color: #fcfbf9;
    }
    h1 {
        color: #8B4513;
        font-family: 'Trebuchet MS', sans-serif;
    }
    h3 {
        color: #D2691E;
    }
    .stButton>button {
        background-color: #D2691E;
        color: white;
        border-radius: 10px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #8B4513;
        color: white;
    }
    .terra-box {
        background-color: #FFF8DC;
        padding: 15px;
        border-radius: 15px;
        border-left: 5px solid #D2691E;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR - FORMULA PINTAS & KALKULATOR
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/illustrations/external-pack-yx-lineal-color-mixed-lineal-color/100/external-Earth-geology-pack-yx-lineal-color-mixed-lineal-color.png", width=80)
    st.title("Pusat Kontrol Terra 🛰️")
    st.write("Hai! Aku **Terra**, asisten belajarmu yang paling ramah. Yuk pilih menu cepat di bawah ini!")

    st.markdown("---")
    st.subheader("🧮 Kalkulator Cepat Geofisika")

    # Dropdown Pilih Rumus
    formula_option = st.selectbox(
        "Pilih Rumus yang Mau Dihitung:",
        ["Hukum Snellius (Refraksi)", "Faktor Geometri K (Schlumberger)", "Hukum Archie (Resistivitas Batuan)"]
    )

    if formula_option == "Hukum Snellius (Refraksi)":
        st.latex(r"\frac{\sin(\theta_1)}{V_1} = \frac{\sin(\theta_2)}{V_2}")
        v1 = st.number_input("Kecepatan Lapisan 1 (V1) m/s", value=1500.0)
        theta1 = st.number_input("Sudut Datang (θ1) derajat", value=30.0, min_value=0.0, max_value=90.0)
        v2 = st.number_input("Kecepatan Lapisan 2 (V2) m/s", value=2500.0)

        # Hitung sudut bias (theta 2)
        sin_theta2 = (v2 / v1) * np.sin(np.radians(theta1))
        if sin_theta2 > 1.0:
            st.warning("⚠️ Terjadi Sudut Kritis! Gelombang merambat sebagai head wave.")
        else:
            theta2 = np.degrees(np.arcsin(sin_theta2))
            st.success(f"Sudut Bias (θ2) = {theta2:.2f}°")

    elif formula_option == "Faktor Geometri K (Schlumberger)":
        st.latex(r"K = \pi \frac{(AB/2)^2 - (MN/2)^2}{MN}")
        ab_2 = st.number_input("Jarak elektroda arus (AB/2) meter", value=10.0, min_value=0.1)
        mn_2 = st.number_input("Jarak elektroda potensial (MN/2) meter", value=1.0, min_value=0.1)

        if ab_2 <= mn_2:
            st.error("❌ AB/2 harus lebih besar dari MN/2 dong!")
        else:
            # Hitung K
            L = ab_2
            b = mn_2
            k_val = (np.pi * (L**2 - b**2)) / (2 * b)
            st.success(f"Faktor Geometri (K) = {k_val:.2f} m")

    elif formula_option == "Hukum Archie (Resistivitas Batuan)":
        st.latex(r"F = \frac{a}{\phi^m}")
        phi = st.slider("Porositas Batuan (φ)", 0.01, 0.5, value=0.2)
        m = st.number_input("Faktor Sementasi (m)", value=2.0)
        a = st.number_input("Konstanta Litologi (a)", value=1.0)

        f_factor = a / (phi**m)
        st.success(f"Faktor Formasi (F) = {f_factor:.2f}")

    st.markdown("---")
    st.info("💡 **Tips Terra:** Gunakan kalkulator di atas untuk memverifikasi hitungan manual laporan praktikummu ya!")

# ==========================================
# 3. HALAMAN UTAMA - UTILITY & CHAT
# ==========================================

# Banner Selamat Datang
st.title("🌍 Terra: Asisten Ahli Geofisika & Energi")
st.markdown(
    """
    <div class="terra-box">
    <h4>Halo, Sobat Geofisika! 👋 🦖</h4>
    Aku <b>Terra</b>! Di sini aku siap nemenin kamu belajar fisika bumi, menganalisis data lapangan, 
    atau sekadar curhat tentang praktikum yang melelahkan. Nggak usah sungkan, kita santai aja ya!
    </div>
    """, 
    unsafe_allow_html=True
)

# Pembuatan Kolom: Kolom Kiri untuk upload data, Kolom Kanan untuk Chat
col1, col2 = st.columns([1.1, 1.0])

# --- KOLOM 1: ANALISIS DATA OTOMATIS (CSV) ---
with col1:
    st.subheader("📊 Laboratorium Data Terra")
    st.write("Punya data hasil praktikum/lapangan? Upload file CSV-mu di sini, nanti aku bantu plot dan analisis!")

    # Tombol Download Template CSV untuk testing
    test_data_type = st.radio("Pilih jenis template data uji coba:", ["Geolistrik (VES)", "Seismik Refraksi"])

    if test_data_type == "Geolistrik (VES)":
        df_temp = pd.DataFrame({
            'AB_2': [1, 2, 3, 4, 6, 8, 10, 15, 20],
            'App_Resistivity': [120, 115, 95, 70, 45, 55, 80, 110, 130]
        })
    else:
        df_temp = pd.DataFrame({
            'Distance_m': [5, 10, 15, 20, 25, 30, 35, 40],
            'TravelTime_ms': [12, 24, 35, 42, 48, 54, 60, 66]
        })

    csv_buffer = io.StringIO()
    df_temp.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download Template Data CSV",
        data=csv_buffer.getvalue(),
        file_name=f"template_{test_data_type.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )

    uploaded_file = st.file_uploader("Unggah file CSV kamu di sini:", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("🟢 **Pratinjau Data Kamu:**")
            st.dataframe(df.head(5))

            # Deteksi Kolom Otomatis untuk Plotting
            cols = df.columns.tolist()
            st.success(f"Berhasil membaca data dengan kolom: {', '.join(cols)}")

            # Buat Visualisasi Otomatis
            fig, ax = plt.subplots(figsize=(6, 4))

            # Skenario 1: Data Geolistrik (AB/2 vs Resistivitas Semu) -> Log-Log Plot
            if any('ab' in col.lower() for col in cols) or any('res' in col.lower() for col in cols):
                x_col = [col for col in cols if 'ab' in col.lower()][0]
                y_col = [col for col in cols if 'res' in col.lower()][0]

                ax.loglog(df[x_col], df[y_col], 'o-', color='#D2691E', label="Data VES")
                ax.set_xlabel(f"Sensus Jarak {x_col} (m)")
                ax.set_ylabel(f"Resistivitas Semu {y_col} (Ohm.m)")
                ax.grid(True, which="both", ls="--")
                ax.legend()
                st.pyplot(fig)

                # Analisis Singkat dari Terra
                st.markdown("""
                    **🔍 Analisis Awal Terra:**
                    *   Grafik ini digambar dalam skala log-log (sangat cocok untuk kurva VES).
                    *   Terlihat adanya tren perubahan resistivitas terhadap kedalaman (AB/2). 
                    *   Jika kurva turun lalu naik kembali, kemungkinan kamu mendeteksi adanya lapisan konduktif (seperti lempung/air tanah) di bagian tengah, diikuti oleh lapisan keras (basement/batu pasir kering) di bagian bawah!
                """)

            # Skenario 2: Data Seismik (Jarak vs Waktu Tiba) -> Linier Plot
            elif any('dist' in col.lower() or 'x' in col.lower() for col in cols):
                x_col = [col for col in cols if 'dist' in col.lower() or 'x' in col.lower()][0]
                y_col = [col for col in cols if 'time' in col.lower() or 't' in col.lower()][0]

                ax.plot(df[x_col], df[y_col], 's--', color='#4682B4', label="T-X Data")
                ax.set_xlabel(f"Jarak Penerima {x_col} (m)")
                ax.set_ylabel(f"Waktu Tiba {y_col} (ms)")
                ax.grid(True)
                ax.legend()
                st.pyplot(fig)

                # Analisis Singkat dari Terra
                st.markdown("""
                    **🔍 Analisis Awal Terra:**
                    *   Ini adalah grafik hubungan jarak penerima (*geophone*) terhadap waktu tiba gelombang (*travel time*).
                    *   Perubahan kemiringan (slope) pada grafik ini menandakan adanya batas lapisan bawah permukaan bumi dengan kecepatan (*velocity*) yang berbeda.
                    *   Semakin landai garisnya, semakin cepat gelombang merambat di lapisan tersebut!
                """)
            else:
                # Plot standar jika tidak terdeteksi kolom khusus
                ax.plot(df.iloc[:, 0], df.iloc[:, 1], 'o-')
                ax.set_xlabel(cols[0])
                ax.set_ylabel(cols[1])
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Aduh, ada error sedikit pas baca file: {e}")

# --- KOLOM 2: CHAT INTERAKTIF DENGAN TERRA ---
with col2:
    st.subheader("💬 Ngobrol Santai bareng Terra")

    # Inisialisasi Riwayat Chat di Streamlit
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Halo! Aku Terra. Ada kesulitan tentang konsep geofisika, coding inversi, atau tugas kuliah hari ini? Tumpahkan semuanya di sini, yuk kita selesaikan bareng! 🤗✨"}
        ]

    # Menampilkan riwayat chat sebelumnya
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input dari Pengguna
    if user_query := st.chat_input("Tanya apa saja ke Terra..."):
        # Tambahkan pertanyaan user ke riwayat chat
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Logika Sederhana Respon Terra (Bisa diintegrasikan ke API OpenAI/Gemini milikmu nanti)
        with st.chat_message("assistant"):
            response_placeholder = st.empty()

            # Contoh respon cerdas & ramah berbasis kata kunci (mock-up sebelum dihubungkan ke LLM API)
            query_lower = user_query.lower()
            if "seismik" in query_lower:
                reply = "Wah, bahas seismik nih! Gelombang seismik itu keren banget, kayak USG buat bumi. Ada gelombang badan (P & S) dan gelombang permukaan. Bagian mana nih yang bikin kamu penasaran? Metodologi akuisisi, *processing* data, atau interpretasi strukturnya? 🌋"
            elif "geolistrik" in query_lower or "resistivitas" in query_lower:
                reply = "Aha! Geolistrik resistivitas! Metode andalan buat nyari air tanah (akuifer) atau batuan dasar. Kita mengalirkan arus listrik lewat elektroda lalu mengukur beda potensialnya. Mau bahas konfigurasi Wenner, Schlumberger, atau Dipole-dipole? ⚡"
            elif "inversi" in query_lower or "coding" in query_lower:
                reply = "Asyik, mainan coding komputasi geofisika! 💻 Biasanya kita pakai Python (pustaka Numpy/Scipy) buat nyari kecocokan model (*misfit* terkecil) lewat metode *Least-Squares*. Butuh contoh script sederhana untuk inversi linear 1D kah? Katakan saja!"
            elif "geothermal" in query_lower or "panas bumi" in query_lower:
                reply = "Geothermal! Harta karun energi bersih Indonesia yang melimpah ruah! 🌿 Di sini geofisika berperan penting buat cari *heat source*, reservoir, dan mendeteksi lapisan penudung (*clay cap*) pakai metode Magnetotellurik (MT). Ada tugas tentang sistem hidrotermal ya? Let's go kita bahas!"
            else:
                reply = f"Pertanyaan yang menarik banget! Hubungan geofisikanya kuat sekali ini. Biar lebih asyik, yuk coba kita bedah dari konsep dasarnya dulu, lalu kita hubungkan ke aplikasi riilnya di lapangan. Gimana, siap kuliti topiknya bareng Terra? 🚀"

            response_placeholder.markdown(reply)
            # Simpan respon Terra ke riwayat chat
            st.session_state.messages.append({"role": "assistant", "content": reply})
