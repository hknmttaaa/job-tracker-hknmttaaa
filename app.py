from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Halaman & Tema Warna Gelap Angkasa
st.set_page_config(
    page_title="Job Application Tracker - Space Theme",
    page_icon="🚀",
    layout="wide",
)

# Custom CSS untuk tema Biru Gelap / Angkasa yang elegan
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #0b132b, #1c2541, #3a506b);
        color: #ffffff;
    }
    .metric-card {
        background-color: rgba(28, 37, 65, 0.7);
        border: 1px solid #48cae4;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🚀 Space Job Application Tracker")
st.write(
    "Pantau progres lamaran kerja kamu dengan mudah, interaktif, dan real-time!"
)

# Simulasi koneksi data sederhana (bisa dihubungkan ke Google Sheets via gspread/st-connection nanti)
# Untuk tahap awal kita sediakan form input interaktif CRUD lengkap.

# Sidebar untuk Input Data Baru (Create)
st.sidebar.header("📝 Input Lamaran Baru")
with st.sidebar.form("add_form"):
    sosmed = st.text_input("Sosial Media Perusahaan")
    perusahaan = st.text_input("Nama Perusahaan")
    tgl_lamar = st.date_input("Tanggal Lamar", datetime.today())
    jenis_lamaran = st.selectbox("Jenis Lamaran", ["Gform", "Website"])
    posisi = st.text_input("Posisi")
    dokumen_via = st.selectbox("Dokumen Via", ["Gform", "Website"])
    nemu_loker = st.selectbox(
        "Nemu Loker Di",
        ["LinkedIn", "Jobstreet", "Instagram", "Telegram", "Lainnya"],
    )
    durasi_kontrak = st.text_input("Durasi Kontrak (Cth: 1 Tahun / Tetap)")
    jenis_kerja = st.selectbox("Jenis Kerja", ["Hybrid", "WFO", "WFH"])
    tgl_pengumuman = st.date_input(
        "Tanggal Pengumuman Berakhir", datetime.today()
    )
    hasil = st.selectbox(
        "Hasil",
        [
            "PENDING / MENUNGGU",
            "LOLOS ADMINISTRASI",
            "LOLOS WAWANCARA HRD",
            "LOLOS WAWANCARA USER",
            "LOLOS (BERHASIL)",
            "TIDAK LOLOS",
        ],
    )
    evaluasi = st.text_area("Evaluasi / Catatan")

    submit_button = st.form_submit_button(label="Simpan Data")

    if submit_button:
        st.success(f"Data lamaran untuk {perusahaan} berhasil disimpan!")

# --- DASHBOARD UTAMA ---
# Data Dummy / Contoh Tampilan Tabel (Nanti otomatis tersinkron dengan inputan/database)
data_dummy = pd.DataFrame(
    {
        "Sosial Media": ["@hrd_ptA", "@karir_ptB", "@ptC_official"],
        "Nama Perusahaan": ["PT Alpha", "PT Beta", "PT Gamma"],
        "Tanggal Lamar": ["2026-09-01", "2026-09-10", "2026-09-15"],
        "Jenis Lamaran": ["Gform", "Website", "Gform"],
        "Posisi": ["Data Entry", "Data Analyst", "Python Developer"],
        "Dokumen Via": ["Gform", "Website", "Gform"],
        "Nemu Loker Di": ["LinkedIn", "Jobstreet", "LinkedIn"],
        "Durasi Kontrak": ["1 Tahun", "Tetap", "1 Tahun"],
        "Jenis Kerja": ["WFO", "Hybrid", "WFH"],
        "Tanggal Pengumuman Berakhir": [
            "2026-09-20",
            "2026-09-30",
            "2026-10-05",
        ],
        "Hasil": ["LOLOS ADMINISTRASI", "PENDING / MENUNGGU", "TIDAK LOLOS"],
        "Evaluasi": ["Lanjut tes psikotes", "Menunggu kabar email", "Kurang di portofolio"],
    }
)

# 1. Metrik Ringkasan Atas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Total Lamaran", value=len(data_dummy), delta="Aktif Melamar"
    )
with col2:
    pending_count = len(
        data_dummy[data_dummy["Hasil"].str.contains("PENDING", na=False)]
    )
    st.metric(label="Pending / Menunggu", value=pending_count)
with col3:
    lolos_count = len(
        data_dummy[data_dummy["Hasil"].str.contains("LOLOS", na=False)]
    )
    st.metric(label="Lolos / Berhasil", value=lolos_count)
with col4:
    gagal_count = len(
        data_dummy[data_dummy["Hasil"].str.contains("TIDAK LOLOS", na=False)]
    )
    st.metric(label="Gagal / Tidak Lolos", value=gagal_count)

st.markdown("---")

# 2. Grafik Interaktif
st.subheader("📊 Statistik Status Lamaran")
col_g1, col_g2 = st.columns(2)

with col_g1:
    fig_status = px.pie(
        data_dummy,
        names="Hasil",
        title="Distribusi Hasil Lamaran",
        color_discrete_sequence=px.colors.sequential.Tealgrn,
    )
    fig_status.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_status, use_container_width=True)

with col_g2:
    fig_platform = px.bar(
        data_dummy,
        x="Nemu Loker Di",
        title="Sumber Platform Loker Paling Sering Digunakan",
        color="Nemu Loker Di",
    )
    fig_platform.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_platform, use_container_width=True)

# 3. Tabel Data & Fitur Edit/Hapus (CRUD Read & Update preview)
st.subheader("📋 Daftar Seluruh Lamaran Kerja")
st.dataframe(data_dummy, use_container_width=True)