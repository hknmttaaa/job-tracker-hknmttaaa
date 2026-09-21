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

# Custom CSS: Tema Angkasa, Ukuran Kartu Metrik Besar Kembali Seperti Semula
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

    /* Mengembalikan ukuran tinggi dan tampilan tombol kartu metrik atas agar besar seperti semula */
    div.metric-all button,
    div.metric-pending button,
    div.metric-lolos button,
    div.metric-gagal button {
        width: 100% !important;
        height: 95px !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        font-weight: 700 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s ease-in-out;
    }

    div.metric-all button { background: linear-gradient(135deg, #2980b9, #3498db) !important; }
    div.metric-pending button { background: linear-gradient(135deg, #f39c12, #d35400) !important; }
    div.metric-lolos button { background: linear-gradient(135deg, #27ae60, #2ecc71) !important; }
    div.metric-gagal button { background: linear-gradient(135deg, #c0392b, #e74c3c) !important; }

    div[class*="metric-"] button:hover {
        transform: translateY(-2px);
        filter: brightness(1.1);
    }

    /* Styling tombol pop-up kecil di bawah */
    .stButton > button {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out;
    }
    
    .stButton > button:hover {
        background-color: #334155 !important;
        color: #ffffff !important;
        border-color: #38bdf8 !important;
    }

    div.element-container:has(iframe) {
        animation: smoothChartEntry 1s cubic-bezier(0.25, 1, 0.5, 1);
    }

    @keyframes smoothChartEntry {
        0% { opacity: 0; transform: scale(0.95) translateY(12px); }
        100% { opacity: 1; transform: scale(1) translateY(0); }
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

    total_lamaran = len(df)
    pending_df = df[df["Hasil"].str.contains("PENDING|MENUNGGU", case=False, na=False)]
    lolos_df = df[df["Hasil"].str.contains("LOLOS|BERHASIL", case=False, na=False)]
    gagal_df = df[df["Hasil"].str.contains("TIDAK LOLOS|GAGAL", case=False, na=False)]

    pending_count = len(pending_df)
    lolos_count = len(lolos_df)
    gagal_count = len(gagal_df)

    # 4 Kolom Kartu Metrik Atas (Ukurannya kembali besar dan berfungsi sebagai tombol pengubah grafik)
    mcol1, mcol2, mcol3, mcol4 = st.columns(4)

    with mcol1:
        st.markdown('<div class="metric-all">', unsafe_allow_html=True)
        btn_chart_all = st.button(f"TOTAL LAMARAN\n\n{total_lamaran}", key="chart_all", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        popup_all = st.button("📁 Lihat Semua", use_container_width=True)

    with mcol2:
        st.markdown('<div class="metric-pending">', unsafe_allow_html=True)
        btn_chart_pending = st.button(f"PENDING / PROSES\n\n{pending_count}", key="chart_pending", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        popup_pending = st.button("⏳ Lihat Pending", use_container_width=True)

    with mcol3:
        st.markdown('<div class="metric-lolos">', unsafe_allow_html=True)
        btn_chart_lolos = st.button(f"LOLOS / BERHASIL\n\n{lolos_count}", key="chart_lolos", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        popup_lolos = st.button("✅ Lihat Lolos", use_container_width=True)

    with mcol4:
        st.markdown('<div class="metric-gagal">', unsafe_allow_html=True)
        btn_chart_gagal = st.button(f"GAGAL / DITOLAK\n\n{gagal_count}", key="chart_gagal", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        popup_gagal = st.button("❌ Lihat Gagal", use_container_width=True)

    # Logika Perubahan Grafik Berdasarkan Tombol Kotak Atas
    if btn_chart_all:
        st.session_state.active_view = "ALL"
    elif btn_chart_pending:
        st.session_state.active_view = "PENDING"
    elif btn_chart_lolos:
        st.session_state.active_view = "LOLOS"
    elif btn_chart_gagal:
        st.session_state.active_view = "GAGAL"

    def safe_display_df(data_frame):
        available_cols = [c for c in ["Perusahaan", "Posisi", "Tanggal Lamar", "Nemu Loker Di", "Jenis Lamaran", "Hasil"] if c in data_frame.columns]
        if available_cols:
            st.dataframe(data_frame[available_cols], use_container_width=True)
        else:
            st.dataframe(data_frame, use_container_width=True)

    # --- POP-UP LIST DETAIL DATA (Dipicu oleh tombol kecil di bawah) ---
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
        safe_display_df(df)

    @st.dialog("⏳ Daftar Lamaran Tahap Pending / Proses", width="large")
    def show_pending_list():
        st.write(f"Total data pending saat ini: **{pending_count}** perusahaan")
        if not pending_df.empty:
            safe_display_df(pending_df)
        else:
            st.info("Tidak ada data lamaran dengan status pending.")

    @st.dialog("✅ Daftar Lamaran Tahap Lolos / Berhasil", width="large")
    def show_lolos_list():
        st.write(f"Total data lolos saat ini: **{lolos_count}** perusahaan 🎉")
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

    # Trigger pop-up ketika tombol teks di bawah ditekan
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
        st.subheader("⏳ Analisis & Statistik Distribusi (Khusus Pending / Proses)")
    elif current_mode == "LOLOS":
        st.subheader("✅ Analisis & Statistik Distribusi (Khusus Lolos / Berhasil)")
    elif current_mode == "GAGAL":
        st.subheader("❌ Analisis & Statistik Distribusi (Khusus Gagal / Ditolak)")

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
                textinfo='none', 
                hoverinfo='label+percent+value',
                rotation=45, 
                pull=[0.05 if i == 0 else 0 for i in range(len(active_chart_df['Hasil'].unique()))]
            )
            fig_status.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                plot_bgcolor="rgba(0,0,0,0)",
                title_font_size=16,
                transition_duration=1000
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info(f"Tidak ada data untuk kategori {current_mode}.")

    with gcol2:
        if not active_chart_df.empty and "Nemu Loker Di" in active_chart_df.columns:
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
                transition_duration=1000
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
        platforms = ["Semua"] + list(df["Nemu Loker Di"].unique()) if "Nemu Loker Di" in df.columns else ["Semua"]
        selected_platform = st.selectbox("📌 Filter Sumber Platform", platforms)

    with fcol3:
        work_types = ["Semua"] + list(df["Jenis Kerja"].unique()) if "Jenis Kerja" in df.columns else ["Semua"]
        selected_work_type = st.selectbox("💼 Filter Jenis Kerja", work_types)

    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[
            filtered_df.astype(str)
            .apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        ]

    if selected_platform != "Semua" and "Nemu Loker Di" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Nemu Loker Di"] == selected_platform]

    if selected_work_type != "Semua" and "Jenis Kerja" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Jenis Kerja"] == selected_work_type]

    st.dataframe(filtered_df, use_container_width=True)
    st.caption(f"Menampilkan {len(filtered_df)} dari total {len(df)} data lamaran.")

else:
    st.info(
        "🚀 Belum ada data atau Google Sheets masih kosong. Silakan input data lamaran pertamamu lewat sidebar di sebelah kiri!"
    )
