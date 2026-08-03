import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# ==========================================
# 1. KONFIGURASI TAMPILAN WEB
# ==========================================
st.set_page_config(page_title="Terra - AI Geofisika", page_icon="🌍", layout="centered")
st.title("🌍 Terra: Asisten AI Geofisika")
st.caption("Halo! Aku Terra, siap membantumu menerjemahkan rumus bumi ke dalam kode.")

# ==========================================
# 2. INSTRUKSI SISTEM (PERSONA TERRA)
# ==========================================
instruksi_terra = """
Kamu adalah Terra, sesosok maskot dan asisten ahli pemrograman Teknik Geofisika yang cerdas, sabar, dan ramah. 
Target audiensmu adalah Mahasiswa Baru (Maba) yang belum punya dasar coding yang kuat.

Saat merespon pertanyaan, kamu WAJIB mengikuti alur PROSES dan OUTPUT berikut:
1. Analisis Logika Fisika: Jelaskan konsep geofisika secara singkat dari masalah tersebut.
2. Pemilihan Alat/Library: Sebutkan library yang dipakai (misal NumPy, Pandas, Matplotlib) dan alasannya.
3. Pemecahan Algoritma: Berikan langkah-langkah logika step-by-step.
4. Blok Kode (Code Block): Berikan kode yang bersih dengan komentar pada setiap baris penting.
5. Ekspektasi Output Visual: Jelaskan hasil apa yang akan muncul.

Jika user mengunggah data, perhatikan cuplikan data tersebut untuk memberikan analisis kode yang lebih akurat.
Selalu gunakan nada bicara yang hangat dan suportif layaknya teman.
"""

# ==========================================
# 3. SIDEBAR & FITUR UPLOAD
# ==========================================
# Mengambil kunci dari brankas rahasia Streamlit Cloud secara otomatis
api_key = st.secrets["GEMINI_API_KEY"]

# Variabel untuk menyimpan cuplikan data dari file
konteks_data = ""

with st.sidebar:
    st.header("📂 Upload Data (Opsional)")
    uploaded_file = st.file_uploader("Upload file data Geofisika", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Berhasil membaca: {uploaded_file.name}")
            st.write("Preview Data (5 baris pertama):")
            st.dataframe(df.head())
            
            # Menyimpan cuplikan data agar bisa dibaca oleh Terra
            konteks_data = f"\n\n[INFO UNTUK TERRA: User telah mengunggah file data. Berikut adalah 5 baris pertama dari data tersebut:\n{df.head().to_string()}]"
        except Exception as e:
            st.error("Gagal membaca file. Pastikan formatnya CSV.")
    
    st.divider()
    st.header("⚙️ Pengaturan")
    st.success("✅ Terra Terhubung ke Server")
    
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
if prompt := st.chat_input("Tanya Terra tentang coding / rumus geofisika di sini..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Menggabungkan pertanyaan user dengan data file (jika ada)
    prompt_ke_ai = prompt + konteks_data

    with st.chat_message("assistant"):
        try:
            os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
            os.environ.pop("GOOGLE_API_KEY", None)
            
            genai.configure(api_key=api_key)
            
            # Menggunakan Gemini 3.6
            model = genai.GenerativeModel(
                model_name='gemini-3.6-flash',
                system_instruction=instruksi_terra
            )
            
            history_gemini = []
            for m in st.session_state.messages[:-1]:
                role_gemini = "model" if m["role"] == "assistant" else "user"
                history_gemini.append({"role": role_gemini, "parts": [m["content"]]})
                
            chat = model.start_chat(history=history_gemini)
            
            with st.spinner("Terra sedang menganalisis..."):
                response = chat.send_message(prompt_ke_ai)
                
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("❌ Terjadi kesalahan pada sistem AI.")
            with st.expander("Lihat Detail Error"):
                st.write(str(e))
        except Exception as e:
            st.error("❌ Terjadi kesalahan pada sistem AI.")
            with st.expander("Lihat Detail Error"):
                st.write(str(e))
