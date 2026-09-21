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

# Custom CSS: Membuat tombol Streamlit menyerupai kartu metrik HTML yang estetik
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
    }

    /* Desain persis seperti kartu metrik (Total Lamaran -> Oranye) */
    div.metric-all button {
        background: linear-gradient(135deg, #3498db, #2980b9) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 20px !important;
        height: 110px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        font-weight: 700 !important;
    }

    /* Desain Pending -> Kuning */
    div.metric-pending button {
        background: linear-gradient(135deg, #f39c12, #d35400) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 20px !important;
        height: 110px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        font-weight: 700 !important;
    }

    /* Desain Lolos -> Hijau */
    div.metric-lolos button {
        background: linear-gradient(135deg, #2ecc71, #27ae60) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 20px !important;
        height: 110px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        font-weight: 700 !important;
    }

    /* Desain Gagal -> Merah */
    div.metric-gagal button {
        background: linear-gradient(135deg, #e74c3c, #c0392b) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 20px !important;
        height: 110px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        font-weight: 700 !important;
    }

    div[class*="metric-"] button:hover {
        transform: translateY(-2px);
        filter: brightness(1.1);
        color: white !important;
    }

    /* Tombol teks kecil di bawah */
    .stButton > button {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: #334155 !important;
        color: #ffffff !important;
        border-color: #38bdf8 !important;
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
        <p style="margin: 0; color: #a0aec0; font-size: 16px;">Pusat kendali karier interaktif dengan grafik dinamis dan pemantauan real-time.</p>
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
    df.columns = df.columns.str.strip()
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
if not df.empty and "Hasil" in df.columns:
    if "active_view" not in st.session_state:
    st.session_state.active_view = "ALL"

# Cek interaksi dari klik kartu HTML
query_params = st.query_params
if "set_view" in query_params:
    st.session_state.active_view = query_params["set_view"]

current_mode = st.session_state.active_view

# CSS Khusus Kartu Metrik Estetik & Berwarna
st.markdown(
    """
    <style>
    .metric-grid {
        display: flex;
        gap: 15px;
        width: 100%;
        margin-bottom: 15px;
    }
    .metric-box {
        flex: 1;
        padding: 20px;
        border-radius: 14px;
        color: white;
        text-align: center;
        text-decoration: none !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
        transition: transform 0.2s ease, filter 0.2s ease;
        display: block;
    }
    .metric-box:hover {
        transform: translateY(-3px);
        filter: brightness(1.15);
        color: white !important;
    }
    .box-all { background: linear-gradient(135deg, #3498db, #2980b9); }
    .box-pending { background: linear-gradient(135deg, #f39c12, #d35400); }
    .box-lolos { background: linear-gradient(135deg, #2ecc71, #27ae60); }
    .box-gagal { background: linear-gradient(135deg, #e74c3c, #c0392b); }
    
    .box-title {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    .box-value {
        font-size: 26px;
        font-weight: 800;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Render Kotak Warna-warni (Klik ini untuk mengubah grafik)
st.markdown(
    f"""
    <div class="metric-grid">
        <a href="?set_view=ALL" target="_self" class="metric-box box-all">
            <div class="box-title">TOTAL LAMARAN</div>
            <div class="box-value">{total_lamaran}</div>
        </a>
        <a href="?set_view=PENDING" target="_self" class="metric-box box-pending">
            <div class="box-title">PENDING / PROSES</div>
            <div class="box-value">{pending_count}</div>
        </a>
        <a href="?set_view=LOLOS" target="_self" class="metric-box box-lolos">
            <div class="box-title">LOLOS / BERHASIL</div>
            <div class="box-value">{lolos_count}</div>
        </a>
        <a href="?set_view=GAGAL" target="_self" class="metric-box box-gagal">
            <div class="box-title">GAGAL / DITOLAK</div>
            <div class="box-value">{gagal_count}</div>
        </a>
    </div>
""",
    unsafe_allow_html=True,
)

# Tombol kecil di bawahnya khusus untuk memunculkan pop-up detail data
pcol1, pcol2, pcol3, pcol4 = st.columns(4)
with pcol1:
    popup_all = st.button("📁 Detail Semua", use_container_width=True, key="pop_all")
with pcol2:
    popup_pending = st.button(
        "⏳ Detail Pending", use_container_width=True, key="pop_pen"
    )
with pcol3:
    popup_lolos = st.button(
        "✅ Detail Lolos", use_container_width=True, key="pop_lol"
    )
with pcol4:
    popup_gagal = st.button(
        "❌ Detail Gagal", use_container_width=True, key="pop_gag"
    )

    # Logika Ubah Grafik Berdasarkan Tombol Kartu Atas
    if btn_chart_all:
        st.session_state.active_view = "ALL"
    elif btn_chart_pending:
        st.session_state.active_view = "PENDING"
    elif btn_chart_lolos:
        st.session_state.active_view = "LOLOS"
    elif btn_chart_gagal:
        st.session_state.active_view = "GAGAL"

    def safe_display_df(data_frame):
        available_cols = [
            c
            for c in [
                "Perusahaan",
                "Posisi",
                "Tanggal Lamar",
                "Nemu Loker Di",
                "Jenis Lamaran",
                "Hasil",
            ]
            if c in data_frame.columns
        ]
        if available_cols:
            st.dataframe(
                data_frame[available_cols], use_container_width=True
            )
        else:
            st.dataframe(data_frame, use_container_width=True)

    # --- POP-UP LIST DETAIL DATA (Dipicu tombol kecil di bawah) ---
    @st.dialog("📊 Ringkasan Keseluruhan Lamaran", width="large")
    def show_all_summary():
        st.write(f"### Total Perusahaan Dilamar: **{total_lamaran}**")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.write("📌 **Distribusi Jenis Lamaran:**")
            if "Jenis Lamaran" in df.columns:
                st.dataframe(
                    df["Jenis Lamaran"].value_counts().reset_index(),
                    use_container_width=True,
                    hide_index=True,
                )
        with col_s2:
            st.write("💼 **Daftar Posisi yang Dilamar:**")
            if "Posisi" in df.columns:
                st.dataframe(
                    df["Posisi"].value_counts().reset_index(),
                    use_container_width=True,
                    hide_index=True,
                )
        st.write("📋 **Seluruh Data Perusahaan:**")
        safe_display_df(df)

    @st.dialog("⏳ Daftar Lamaran Tahap Pending / Proses", width="large")
    def show_pending_list():
        st.write(
            f"Total data pending saat ini: **{pending_count}** perusahaan"
        )
        if not pending_df.empty:
            safe_display_df(pending_df)
        else:
            st.info("Tidak ada data lamaran dengan status pending.")

    @st.dialog("✅ Daftar Lamaran Tahap Lolos / Berhasil", width="large")
    def show_lolos_list():
        st.write(
            f"Total data lolos saat ini: **{lolos_count}** perusahaan 🎉"
        )
        if not lolos_df.empty:
            safe_display_df(lolos_df)
        else:
            st.info("Belum ada data lamaran yang lolos.")

    @st.dialog("❌ Daftar Lamaran Tahap Gagal / Ditolak", width="large")
    def show_gagal_list():
        st.write(f"Total data gagal saat ini: **{gagal_count}** perusahaan")
        if not gagal_df.empty:
            safe_display_df(gagal_df)
        else:
            st.info("Tidak ada data lamaran yang gagal.")

    if popup_all:
        show_all_summary()
    elif popup_pending:
        show_pending_list()
    elif popup_lolos:
        show_lolos_list()
    elif popup_gagal:
        show_gagal_list()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- BAGIAN GRAFIK INTERAKTIF DINAMIS ---
    current_mode = st.session_state.active_view
    if current_mode == "ALL":
        st.subheader("📊 Analisis & Statistik Distribusi (Semua Lamaran)")
    elif current_mode == "PENDING":
        st.subheader(
            "⏳ Analisis & Statistik Distribusi (Khusus Pending / Proses)"
        )
    elif current_mode == "LOLOS":
        st.subheader(
            "✅ Analisis & Statistik Distribusi (Khusus Lolos / Berhasil)"
        )
    elif current_mode == "GAGAL":
        st.subheader(
            "❌ Analisis & Statistik Distribusi (Khusus Gagal / Ditolak)"
        )

    gcol1, gcol2 = st.columns(2)

    if current_mode == "PENDING":
        active_chart_df = pending_df
    elif current_mode == "LOLOS":
        active_chart_df = lolos_df
    elif current_mode == "GAGAL":
        active_chart_df = gagal_df
    else:
        active_chart_df = df

    with gcol1:
        if not active_chart_df.empty and "Hasil" in active_chart_df.columns:
            fig_status = px.pie(
                active_chart_df,
                names="Hasil",
                title=f"Proporsi Status ({current_mode})",
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig_status.update_traces(
                textinfo="none",
                hoverinfo="label+percent+value",
                rotation=45,
            )
            fig_status.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                plot_bgcolor="rgba(0,0,0,0)",
                title_font_size=16,
                transition_duration=1000,
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info(f"Tidak ada data untuk kategori {current_mode}.")

    with gcol2:
        if (
            not active_chart_df.empty
            and "Nemu Loker Di" in active_chart_df.columns
        ):
            fig_platform = px.bar(
                active_chart_df,
                x="Nemu Loker Di",
                title=f"Sumber Platform Loker ({current_mode})",
                color="Nemu Loker Di",
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig_platform.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                plot_bgcolor="rgba(0,0,0,0)",
                title_font_size=16,
                showlegend=False,
                transition_duration=1000,
            )
            st.plotly_chart(fig_platform, use_container_width=True)
        else:
            st.info(f"Tidak ada data platform untuk kategori {current_mode}.")

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
        platforms = (
            ["Semua"] + list(df["Nemu Loker Di"].unique())
            if "Nemu Loker Di" in df.columns
            else ["Semua"]
        )
        selected_platform = st.selectbox("📌 Filter Sumber Platform", platforms)

    with fcol3:
        work_types = (
            ["Semua"] + list(df["Jenis Kerja"].unique())
            if "Jenis Kerja" in df.columns
            else ["Semua"]
        )
        selected_work_type = st.selectbox("💼 Filter Jenis Kerja", work_types)

    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[
            filtered_df.astype(str)
            .apply(
                lambda row: row.str.contains(search_query, case=False).any(),
                axis=1,
            )
        ]

    if (
        selected_platform != "Semua"
        and "Nemu Loker Di" in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df["Nemu Loker Di"] == selected_platform
        ]

    if selected_work_type != "Semua" and "Jenis Kerja" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["Jenis Kerja"] == selected_work_type
        ]

    st.dataframe(filtered_df, use_container_width=True)
    st.caption(
        f"Menampilkan {len(filtered_df)} dari total {len(df)} data lamaran."
    )

else:
    st.info(
        "🚀 Belum ada data atau Google Sheets masih kosong. Silakan input data lamaran pertamamu lewat sidebar di sebelah kiri!"
    )
