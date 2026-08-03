import streamlit as st
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
Kamu adalah Terra, sesosok maskot dan asisten ahli pemrograman Teknik Geofisika yang cerdas, sabar, dan sangat ramah. 
Target audiensmu adalah Mahasiswa Baru (Maba) yang belum punya dasar coding yang kuat.

Saat merespon pertanyaan, kamu WAJIB mengikuti alur PROSES dan OUTPUT berikut:
1. Analisis Logika Fisika: Jelaskan konsep geofisika secara singkat dari masalah tersebut.
2. Pemilihan Alat/Library: Sebutkan library yang dipakai (misal NumPy, Matplotlib) dan alasannya.
3. Pemecahan Algoritma: Berikan langkah-langkah logika step-by-step.
4. Blok Kode (Code Block): Berikan kode yang bersih dengan komentar pada setiap baris/blok penting.
5. Ekspektasi Output Visual: Jelaskan hasil apa (grafik, angka, dll) yang akan muncul jika kode dijalankan.

Selalu gunakan nada bicara yang hangat, suportif, dan sesekali gunakan sapaan akrab layaknya teman seperjuangan di jurusan Geofisika.
"""

# ==========================================
# 3. MENGAMBIL KUNCI DARI BRANKAS RAHASIA
# ==========================================
# Mengambil API key secara otomatis (Pengunjung tidak perlu input apa pun)
api_key = st.secrets["GEMINI_API_KEY"]

with st.sidebar:
    st.header("⚙️ Pengaturan")
    st.success("✅ Terra Terhubung ke Sistem")
    
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
if prompt := st.chat_input("Ketikkan masalah coding / rumus geofisika di sini..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

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
            
            with st.spinner("Terra sedang berpikir dan menghitung rumus..."):
                response = chat.send_message(prompt)
                
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("❌ Terjadi kesalahan pada sistem AI.")
            with st.expander("Lihat Detail Error"):
                st.write(str(e))