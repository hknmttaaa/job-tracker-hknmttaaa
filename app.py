from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import streamlit as st

# Konfigurasi Halaman & Layout Lebar
st.set_page_config(
    page_title="Space Job Application Tracker",
    page_icon="🚀",
    layout="wide",
)

# Custom CSS: Tema Angkasa, Tombol Warna-Warni Kontras, & Styling Modal
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0b132b 0%, #1c2541 50%, #3a506b 100%);
        color: #f8f9fa;
    }

    .hero-container {
        background: rgba(28, 37, 65, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 25px;
        animation: fadeIn 1s ease-in-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .metric-card {
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        margin-bottom: 10px;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        margin-top: 5px;
    }
    .metric-label {
        font-size: 14px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Utama
st.markdown(
    """
    <div class="hero-container">
        <h1>🚀 Space Job Application Tracker</h1>
        <p style="margin: 0; color: #a0aec0; font-size: 16px;">Pusat kendali karier interaktif dengan pop-up ringkasan dan pemantauan real-time.</p>
    </div>
""",
    unsafe_allow_html=True,
)


# Fungsi Koneksi Google Sheets
@st.cache_resource
def init_connection():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = dict(st.secrets["connections"]["gsheets"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client


# Ambil Data dari Spreadsheet
try:
    client = init_connection()
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet = client.open_by_url(sheet_url).worksheet("Sheet1")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(
        f"Gagal terhubung ke Google Sheets. Pastikan format Secrets benar. Error: {e}"
    )
    df = pd.DataFrame()

# Sidebar untuk Input Data Baru
st.sidebar.markdown("<h2>📝 Panel Input Loker</h2>", unsafe_allow_html=True)
with st.sidebar.form("add_form", clear_on_submit=True):
    sosmed = st.text_input("Sosial Media Perusahaan")
    perusahaan = st.text_input("Nama Perusahaan*")
    tgl_lamar = st.date_input("Tanggal Lamar", datetime.today())
    jenis_lamaran = st.selectbox("Jenis Lamaran", ["Gform", "Website", "Email"])
    posisi = st.text_input("Posisi*")
    dokumen_via = st.selectbox("Dokumen Via", ["Gform", "Website", "Email"])
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
        "Status / Hasil",
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

    submit_button = st.form_submit_button(label="Simpan ke Google Sheets 🚀")

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
            st.success(f"Berhasil menyimpan lamaran untuk {perusahaan}!")
            st.rerun()
        else:
            st.warning("Nama Perusahaan dan Posisi wajib diisi!")

# --- DASHBOARD UTAMA ---
if not df.empty:
    # Hitung Statistik
    total_lamaran = len(df)
    pending_df = df[df["Hasil"].str.contains("PENDING|MENUNGGU", case=False, na=False)]
    lolos_df = df[df["Hasil"].str.contains("LOLOS|BERHASIL", case=False, na=False)]
    gagal_df = df[df["Hasil"].str.contains("TIDAK LOLOS|GAGAL", case=False, na=False)]

    pending_count = len(pending_df)
    lolos_count = len(lolos_df)
    gagal_count = len(gagal_df)

    # Tampilkan Kartu Metrik dengan Tombol Berwarna Kontras
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)

    with mcol1:
        st.markdown(
            f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #2980b9, #3498db);">
                <div class="metric-label">Total Lamaran</div>
                <div class="metric-value">{total_lamaran}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
        btn_all = st.button("📁 Lihat Semua", use_container_width=True, type="primary")

    with mcol2:
        st.markdown(
            f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #f39c12, #d35400);">
                <div class="metric-label">Pending / Proses</div>
                <div class="metric-value">{pending_count}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
        btn_pending = st.button("⏳ Lihat Pending", use_container_width=True)

    with mcol3:
        st.markdown(
            f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #27ae60, #2ecc71);">
                <div class="metric-label">Lolos / Berhasil</div>
                <div class="metric-value">{lolos_count}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
        btn_lolos = st.button("✅ Lihat Lolos", use_container_width=True)

    with mcol4:
        st.markdown(
            f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #c0392b, #e74c3c);">
                <div class="metric-label">Gagal / Ditolak</div>
                <div class="metric-value">{gagal_count}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
        btn_gagal = st.button("❌ Lihat Gagal", use_container_width=True)

    # --- DEFINISI POP-UP (MODAL) ---
    @st.dialog("📊 Ringkasan Keseluruhan Lamaran", width="large")
    def show_all_summary():
        st.write(f"### Total Perusahaan Dilamar: **{total_lamaran}**")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.write("📌 **Distribusi Jenis Lamaran:**")
            if "Jenis Lamaran" in df.columns:
                st.dataframe(df["Jenis Lamaran"].value_counts().reset_index(), use_container_width=True, hide_index=True)
        with col_s2:
            st.write("💼 **Daftar Posisi yang Dilamar:**")
            if "Posisi" in df.columns:
                st.dataframe(df["Posisi"].value_counts().reset_index(), use_container_width=True, hide_index=True)
        
        st.write("📋 **Seluruh Data Perusahaan:**")
        st.dataframe(df[["Perusahaan", "Posisi", "Jenis Lamaran", "Hasil"]], use_container_width=True)

    @st.dialog("⏳ Daftar Lamaran Tahap Pending / Proses", width="large")
    def show_pending_list():
        st.write(f"Total data pending saat ini: **{pending_count}** perusahaan")
        if not pending_df.empty:
            st.dataframe(pending_df[["Perusahaan", "Posisi", "Tanggal Lamar", "Nemu Loker Di", "Hasil"]], use_container_width=True)
        else:
            st.info("Tidak ada data lamaran dengan status pending.")

    @st.dialog("✅ Daftar Lamaran Tahap Lolos / Berhasil", width="large")
    def show_lolos_list():
        st.write(f"Total data lolos saat ini: **{lolos_count}** perusahaan 🎉")
        if not lolos_df.empty:
            st.dataframe(lolos_df[["Perusahaan", "Posisi", "Tanggal Lamar", "Nemu Loker Di", "Hasil"]], use_container_width=True)
        else:
            st.info("Belum ada data lamaran yang lolos.")

    @st.dialog("❌ Daftar Lamaran Tahap Gagal / Ditolak", width="large")
    def show_gagal_list():
        st.write(f"Total data gagal saat ini: **{gagal_count}** perusahaan")
        if not gagal_df.empty:
            st.dataframe(gagal_df[["Perusahaan", "Posisi", "Tanggal Lamar", "Nemu Loker Di", "Hasil"]], use_container_width=True)
        else:
            st.info("Tidak ada data lamaran yang gagal.")

    # Trigger Pop-up Berdasarkan Tombol yang Ditekan
    if btn_all:
        show_all_summary()
    if btn_pending:
        show_pending_list()
    if btn_lolos:
        show_lolos_list()
    if btn_gagal:
        show_gagal_list()

    st.markdown("<br>", unsafe_allow_html=True)

    # Grafik Analisis Distribusi
    st.subheader("📊 Analisis & Statistik Distribusi")
    gcol1, gcol2 = st.columns(2)

    with gcol1:
        if "Hasil" in df.columns:
            fig_status = px.pie(
                df,
                names="Hasil",
                title="Proporsi Status Hasil Lamaran",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_status.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                plot_bgcolor="rgba(0,0,0,0)",
                title_font_size=16,
            )
            st.plotly_chart(fig_status, use_container_width=True)

    with gcol2:
        if "Nemu Loker Di" in df.columns:
            fig_platform = px.bar(
                df,
                x="Nemu Loker Di",
                title="Sumber Platform Loker Terfavorit",
                color="Nemu Loker Di",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig_platform.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                plot_bgcolor="rgba(0,0,0,0)",
                title_font_size=16,
                showlegend=False,
            )
            st.plotly_chart(fig_platform, use_container_width=True)

    st.markdown("---")

    # --- BAGIAN FILTER & TABEL KESELURUHAN ---
    st.subheader("📋 Data Keseluruhan Lamaran Kerja")

    fcol1, fcol2, fcol3 = st.columns(3)

    with fcol1:
        search_query = st.text_input(
            "🔍 Cari Perusahaan / Posisi",
            placeholder="Ketik nama...",
        )

    with fcol2:
        platforms = ["Semua"] + list(df["Nemu Loker Di"].unique()) if "Nemu Loker Di" in df.columns else ["Semua"]
        selected_platform = st.selectbox("📌 Filter Sumber Platform", platforms)

    with fcol3:
        work_types = ["Semua"] + list(df["Jenis Kerja"].unique()) if "Jenis Kerja" in df.columns else ["Semua"]
        selected_work_type = st.selectbox("💼 Filter Jenis Kerja", work_types)

    # Logika Pemfilteran Data Tabel Bawah
    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[
            filtered_df.astype(str)
            .apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        ]

    if selected_platform != "Semua":
        filtered_df = filtered_df[filtered_df["Nemu Loker Di"] == selected_platform]

    if selected_work_type != "Semua":
        filtered_df = filtered_df[filtered_df["Jenis Kerja"] == selected_work_type]

    st.dataframe(filtered_df, use_container_width=True)
    st.caption(f"Menampilkan {len(filtered_df)} dari total {len(df)} data lamaran.")

else:
    st.info(
        "🚀 Belum ada data atau Google Sheets masih kosong. Silakan input data lamaran pertamamu lewat sidebar di sebelah kiri!"
    )
