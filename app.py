from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Halaman & Tema Warna Gelap Angkasa
st.set_page_config(
    page_title="Job Application Tracker - Space Theme",
    page_icon="🚀",
    layout="wide",
)

# Custom CSS untuk tema Biru Gelap / Angkasa
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #0b132b, #1c2541, #3a506b);
        color: #ffffff;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🚀 Space Job Application Tracker")
st.write(
    "Pantau progres lamaran kerja kamu secara real-time langsung dari Google Sheets!"
)


# Fungsi Koneksi Google Sheets pakai gspread (Anti-Gagal)
@st.cache_resource
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    # Mengambil secrets dari Streamlit
    creds_dict = dict(st.secrets["connections"]["gsheets"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client


# Ambil Data dari Spreadsheet
try:
    client = init_connection()
    # Sesuaikan nama file spreadsheet kamu di sini
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet = client.open_by_url(sheet_url).worksheet("Sheet1")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(
        f"Gagal terhubung ke Google Sheets. Pastikan format Secrets benar. Error: {e}"
    )
    df = pd.DataFrame()

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

    submit_button = st.form_submit_button(label="Simpan ke Google Sheets")

    if submit_button:
        if perusahaan and posisi:
            new_row = [
                sosmed,
                perusahaan,
                str(tgl_lamar),
                jenis_lamaran,
                posisi,
                dokumen_via,
                nemu_loker,
                durasi_kontrak,
                jenis_kerja,
                str(tgl_pengumuman),
                hasil,
                evaluasi,
            ]
            sheet.append_row(new_row)
            st.success(f"Data lamaran untuk {perusahaan} berhasil disimpan!")
            st.rerun()
        else:
            st.warning("Nama Perusahaan dan Posisi wajib diisi!")

# --- DASHBOARD UTAMA ---
if not df.empty:
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

    st.subheader("📋 Daftar Seluruh Lamaran Kerja")
    st.dataframe(df, use_container_width=True)
else:
    st.info(
        "Belum ada data atau Google Sheets masih kosong. Silakan input data lewat sidebar kiri!"
    )
