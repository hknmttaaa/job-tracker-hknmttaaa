from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_gsheets import GsheetsConnection

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

# 1. Koneksi ke Google Sheets
conn = st.connection("gsheets", type=GsheetsConnection)

# Ambil data dari Google Sheets (pastikan nama tab bawahnya "Sheet1")
try:
    df = conn.read(worksheet="Sheet1", ttl=0)
    df = df.dropna(how="all")
except Exception as e:
    st.error(f"Gagal memuat data dari Google Sheets. Error: {e}")
    df = pd.DataFrame()

# Sidebar untuk Input Data Baru (Create) - Langsung Masuk ke Google Sheets
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

    submit_button = st.form_submit_button(label="Simpan ke Google Sheets")

    if submit_button:
        if perusahaan and posisi:
            new_data = pd.DataFrame(
                [
                    {
                        "Sosial Media": sosmed,
                        "Nama Perusahaan": perusahaan,
                        "Tanggal Lamar": str(tgl_lamar),
                        "Jenis Lamaran": jenis_lamaran,
                        "Posisi": posisi,
                        "Dokumen Via": dokumen_via,
                        "Nemu Loker Di": nemu_loker,
                        "Durasi Kontrak": durasi_kontrak,
                        "Jenis Kerja": jenis_kerja,
                        "Tanggal Pengumuman Berakhir": str(tgl_pengumuman),
                        "Hasil": hasil,
                        "Evaluasi": evaluasi,
                    }
                ]
            )

            # Gabungkan data lama dengan data baru lalu kirim ke Google Sheets
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success(f"Data lamaran untuk {perusahaan} berhasil disimpan!")
            st.rerun()
        else:
            st.warning("Nama Perusahaan dan Posisi wajib diisi!")

# --- DASHBOARD UTAMA ---
if not df.empty:
    # 1. Metrik Ringkasan Atas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total Lamaran", value=len(df), delta="Aktif Melamar"
        )
    with col2:
        pending_count = len(df[df["Hasil"].str.contains("PENDING", na=False)])
        st.metric(label="Pending / Menunggu", value=pending_count)
    with col3:
        lolos_count = len(
            df[
                df["Hasil"].str.contains(
                    "LOLOS|BERHASIL", case=False, na=False
                )
            ]
        )
        st.metric(label="Lolos / Berhasil", value=lolos_count)
    with col4:
        gagal_count = len(
            df[df["Hasil"].str.contains("TIDAK LOLOS", na=False)]
        )
        st.metric(label="Gagal / Tidak Lolos", value=gagal_count)

    st.markdown("---")

    # 2. Grafik Interaktif
    st.subheader("📊 Statistik Status Lamaran")
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        if "Hasil" in df.columns:
            fig_status = px.pie(
                df,
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
        if "Nemu Loker Di" in df.columns:
            fig_platform = px.bar(
                df,
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

    # 3. Tabel Data Keseluruhan
    st.subheader("📋 Daftar Seluruh Lamaran Kerja")
    st.dataframe(df, use_container_width=True)
else:
    st.info(
        "Belum ada data atau Google Sheets masih kosong. Silakan input data lewat sidebar kiri!"
    )
