from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

# Konfigurasi Halaman & Layout Lebar
st.set_page_config(
    page_title="Space Job Application Tracker",
    page_icon="🚀",
    layout="wide",
)

# Custom CSS: Lebar tombol disamakan persis selebar kartu di atasnya
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

    .custom-card {
        padding: 20px;
        border-radius: 14px;
        color: white;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 90px;
        margin-bottom: 0px;
    }
    .card-all { background: linear-gradient(135deg, #3498db, #2980b9); }
    .card-pending { background: linear-gradient(135deg, #f39c12, #d35400); }
    .card-lolos { background: linear-gradient(135deg, #2ecc71, #27ae60); }
    .card-gagal { background: linear-gradient(135deg, #e74c3c, #c0392b); }
    
    .card-title {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.9);
    }
    .card-value {
        font-size: 26px;
        font-weight: 800;
        color: white;
    }

    /* Memaksa tombol Streamlit agar lebar penuh (100%) dan tingginya proporsional */
    div.stButton > button {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        font-weight: 600 !important;
        width: 100% !important;
        min-height: 48px !important;
        padding-top: 12px !important;
        padding-bottom: 12px !important;
        font-size: 14px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: all 0.2s ease-in-out;
    }
    
    div.stButton > button:hover {
        background-color: #334155 !important;
        color: #ffffff !important;
        border-color: #38bdf8 !important;
        transform: translateY(-2px);
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
        <p style="margin: 0; color: #a0aec0; font-size: 16px;">Application Tracker</p>
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


# Ambil Data dari Spreadsheet dengan Penanganan Kolom yang Fleksibel
try:
    client = init_connection()
    sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sheet = client.open_by_url(sheet_url).worksheet("Sheet1")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if not df.empty:
        df.columns = df.columns.astype(str).str.strip()
except Exception as e:
    st.error(
        f"Gagal terhubung ke Google Sheets. Pastikan format Secrets benar. Error: {e}"
    )
    df = pd.DataFrame()

# --- SIDEBAR: NAVIGASI MENU (INPUT, EDIT, DELETE) ---
st.sidebar.markdown("<h2>⚙️ Menu Panel</h2>", unsafe_allow_html=True)
menu_mode = st.sidebar.radio(
    "Pilih Aksi", ["➕ Tambah Data Baru", "✏️ Edit / 🗑️ Hapus Data"]
)

# 1. FORM TAMBAH DATA BARU
if menu_mode == "➕ Tambah Data Baru":
    st.sidebar.markdown("<h3>📝 Panel Input Loker</h3>", unsafe_allow_html=True)
    with st.sidebar.form("add_form", clear_on_submit=True):
        sosmed = st.text_input("Sosial Media Perusahaan")
        perusahaan = st.text_input("Nama Perusahaan*")
        tgl_lamar = st.date_input("Tanggal Lamar", datetime.today())
        jenis_lamaran = st.selectbox(
            "Jenis Lamaran", ["Gform", "Website", "Email"]
        )
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

# 2. FORM EDIT & HAPUS DATA
elif menu_mode == "✏️ Edit / 🗑️ Hapus Data":
    st.sidebar.markdown(
        "<h3>✏️ Panel Edit & Hapus Loker</h3>", unsafe_allow_html=True
    )

    if not df.empty:
        col_perusahaan = next(
            (
                c
                for c in df.columns
                if "perusahaan" in c.lower() or "company" in c.lower()
            ),
            None,
        )
        col_posisi = next(
            (
                c
                for c in df.columns
                if "posisi" in c.lower() or "position" in c.lower()
            ),
            None,
        )

        if col_perusahaan:
            df["Display_Label"] = (
                df.index.astype(str)
                + ". "
                + df[col_perusahaan].astype(str)
                + (
                    " - " + df[col_posisi].astype(str)
                    if col_posisi
                    else ""
                )
            )

            selected_item = st.sidebar.selectbox(
                "Pilih Data yang Ingin Diubah/Hapus", df["Display_Label"]
            )
            selected_idx = int(selected_item.split(".")[0])
            row_data = df.iloc[selected_idx]

            with st.sidebar.form("edit_delete_form"):
                p_val = (
                    str(row_data.get(col_perusahaan, ""))
                    if col_perusahaan
                    else ""
                )
                pos_val = (
                    str(row_data.get(col_posisi, "")) if col_posisi else ""
                )
                st.write(f"**Mengubah Data:** {p_val} ({pos_val})")

                e_sosmed = st.text_input(
                    "Sosial Media Perusahaan",
                    value=str(
                        row_data.get(
                            next(
                                (
                                    c
                                    for c in df.columns
                                    if "sosmed" in c.lower()
                                    or "sosial" in c.lower()
                                ),
                                "",
                            ),
                            "",
                        )
                    ),
                )
                e_perusahaan = st.text_input(
                    "Nama Perusahaan*", value=p_val
                )

                tgl_lamar_col = next(
                    (
                        c
                        for c in df.columns
                        if "tanggal lamar" in c.lower()
                        or "tgl lamar" in c.lower()
                    ),
                    None,
                )
                try:
                    default_date_lamar = datetime.strptime(
                        str(row_data.get(tgl_lamar_col, "")), "%Y-%m-%d"
                    ).date()
                except:
                    default_date_lamar = datetime.today()
                e_tgl_lamar = st.date_input(
                    "Tanggal Lamar", value=default_date_lamar
                )

                jl_options = ["Gform", "Website", "Email"]
                jl_col = next(
                    (c for c in df.columns if "jenis lamaran" in c.lower()),
                    None,
                )
                def_jl = (
                    row_data.get(jl_col, "Gform")
                    if jl_col and row_data.get(jl_col) in jl_options
                    else "Gform"
                )
                e_jenis_lamaran = st.selectbox(
                    "Jenis Lamaran",
                    jl_options,
                    index=jl_options.index(def_jl),
                )

                e_posisi = st.text_input("Posisi*", value=pos_val)

                dv_options = ["Gform", "Website", "Email"]
                dv_col = next(
                    (c for c in df.columns if "dokumen via" in c.lower()), None
                )
                def_dv = (
                    row_data.get(dv_col, "Gform")
                    if dv_col and row_data.get(dv_col) in dv_options
                    else "Gform"
                )
                e_dokumen_via = st.selectbox(
                    "Dokumen Via",
                    dv_options,
                    index=dv_options.index(def_dv),
                )

                nl_options = [
                    "LinkedIn",
                    "Jobstreet",
                    "Instagram",
                    "Telegram",
                    "Lainnya",
                ]
                nl_col = next(
                    (
                        c
                        for c in df.columns
                        if "nemu loker" in c.lower() or "sumber" in c.lower()
                    ),
                    None,
                )
                def_nl = (
                    row_data.get(nl_col, "LinkedIn")
                    if nl_col and row_data.get(nl_col) in nl_options
                    else "LinkedIn"
                )
                e_nemu_loker = st.selectbox(
                    "Nemu Loker Di",
                    nl_options,
                    index=nl_options.index(def_nl),
                )

                dur_col = next(
                    (c for c in df.columns if "durasi kontrak" in c.lower()),
                    None,
                )
                e_durasi_kontrak = st.text_input(
                    "Durasi Kontrak",
                    value=str(row_data.get(dur_col, "")) if dur_col else "",
                )

                jk_options = ["Hybrid", "WFO", "WFH"]
                jk_col = next(
                    (c for c in df.columns if "jenis kerja" in c.lower()), None
                )
                def_jk = (
                    row_data.get(jk_col, "Hybrid")
                    if jk_col and row_data.get(jk_col) in jk_options
                    else "Hybrid"
                )
                e_jenis_kerja = st.selectbox(
                    "Jenis Kerja",
                    jk_options,
                    index=jk_options.index(def_jk),
                )

                tgl_pen_col = next(
                    (
                        c
                        for c in df.columns
                        if "pengumuman" in c.lower() or "berakhir" in c.lower()
                    ),
                    None,
                )
                try:
                    default_date_pengumuman = datetime.strptime(
                        str(row_data.get(tgl_pen_col, "")), "%Y-%m-%d"
                    ).date()
                except:
                    default_date_pengumuman = datetime.today()
                e_tgl_pengumuman = st.date_input(
                    "Tanggal Pengumuman Berakhir",
                    value=default_date_pengumuman,
                )

                hasil_options = [
                    "PENDING / MENUNGGU",
                    "LOLOS ADMINISTRASI",
                    "LOLOS WAWANCARA HRD",
                    "LOLOS WAWANCARA USER",
                    "LOLOS (BERHASIL)",
                    "TIDAK LOLOS",
                ]
                hasil_col = next(
                    (
                        c
                        for c in df.columns
                        if c.lower() == "hasil" or "status" in c.lower()
                    ),
                    None,
                )
                def_hasil = (
                    row_data.get(hasil_col, "PENDING / MENUNGGU")
                    if hasil_col
                    and row_data.get(hasil_col) in hasil_options
                    else "PENDING / MENUNGGU"
                )
                e_hasil = st.selectbox(
                    "Status / Hasil",
                    hasil_options,
                    index=hasil_options.index(def_hasil),
                )

                eval_col = next(
                    (
                        c
                        for c in df.columns
                        if "evaluasi" in c.lower() or "catatan" in c.lower()
                    ),
                    None,
                )
                e_evaluasi = st.text_area(
                    "Evaluasi / Catatan",
                    value=str(row_data.get(eval_col, "")) if eval_col else "",
                )

                col_sub1, col_sub2 = st.columns(2)
                update_btn = col_sub1.form_submit_button(label="💾 Update Data")
                delete_btn = col_sub2.form_submit_button(label="🗑️ Hapus Data")

                sheet_row_number = selected_idx + 2

                if update_btn:
                    if e_perusahaan and e_posisi:
                        updated_row = [
                            e_sosmed,
                            e_perusahaan,
                            str(e_tgl_lamar),
                            e_jenis_lamaran,
                            e_posisi,
                            e_dokumen_via,
                            e_nemu_loker,
                            e_durasi_kontrak,
                            e_jenis_kerja,
                            str(e_tgl_pengumuman),
                            e_hasil,
                            e_evaluasi,
                        ]
                        sheet.update(
                            f"A{sheet_row_number}:L{sheet_row_number}",
                            [updated_row],
                        )
                        st.success(
                            f"Berhasil memperbarui data untuk {e_perusahaan}!"
                        )
                        st.rerun()
                    else:
                        st.warning("Nama Perusahaan dan Posisi wajib diisi!")

                if delete_btn:
                    sheet.delete_rows(sheet_row_number)
                    st.success(
                        f"Berhasil menghapus data lamaran untuk {row_data[col_perusahaan]}!"
                    )
                    st.rerun()
        else:
            st.sidebar.warning(
                "Kolom 'Perusahaan' tidak ditemukan di Google Sheets."
            )
    else:
        st.sidebar.info("Tidak ada data di Google Sheets.")


# --- DASHBOARD UTAMA (KARTU METRIK & TOMBOL DETAIL DI BAWAHNYA) ---
hasil_col_main = next(
    (c for c in df.columns if c.lower() == "hasil" or "status" in c.lower()),
    None,
)

if not df.empty and hasil_col_main:
    total_lamaran = len(df)
    pending_df = df[
        df[hasil_col_main].str.contains(
            "PENDING|MENUNGGU", case=False, na=False
        )
    ]
    lolos_df = df[
        df[hasil_col_main].str.contains("LOLOS|BERHASIL", case=False, na=False)
    ]
    gagal_df = df[
        df[hasil_col_main].str.contains("TIDAK LOLOS|GAGAL", case=False, na=False)
    ]

    pending_count = len(pending_df)
    lolos_count = len(lolos_df)
    gagal_count = len(gagal_df)

    # 1. 4 Kolom Kartu Metrik Estetik Berwarna
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    with col_m1:
        st.markdown(
            f"""
            <div class="custom-card card-all">
                <div class="card-title">TOTAL LAMARAN</div>
                <div class="card-value">{total_lamaran}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col_m2:
        st.markdown(
            f"""
            <div class="custom-card card-pending">
                <div class="card-title">PENDING / PROSES</div>
                <div class="card-value">{pending_count}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col_m3:
        st.markdown(
            f"""
            <div class="custom-card card-lolos">
                <div class="card-title">LOLOS / BERHASIL</div>
                <div class="card-value">{lolos_count}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col_m4:
        st.markdown(
            f"""
            <div class="custom-card card-gagal">
                <div class="card-title">GAGAL / DITOLAK</div>
                <div class="card-value">{gagal_count}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    # Spasi kecil agar tidak terlalu mepet kartu metrik
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # 2. Baris Tombol Detail di Bawah Kartu Metrik (Lebar Penuh 100% Mengikuti Kolom Di Atasnya)
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)

    with col_b1:
        btn_detail_semua = st.button("📁 Detail Semua", use_container_width=True)
    with col_b2:
        btn_detail_pending = st.button(
            "⏳ Detail Pending", use_container_width=True
        )
    with col_b3:
        btn_detail_lolos = st.button("✅ Detail Lolos", use_container_width=True)
    with col_b4:
        btn_detail_gagal = st.button("❌ Detail Gagal", use_container_width=True)

    # Logika Tampilan Dialog/Popup Berdasarkan Tombol Detail yang Ditekan
    if btn_detail_semua:

        @st.dialog("📁 Rincian Semua Lamaran", width="large")
        def show_all():
            st.dataframe(df, use_container_width=True)

        show_all()

    elif btn_detail_pending:

        @st.dialog("⏳ Rincian Lamaran Pending", width="large")
        def show_pending():
            if not pending_df.empty:
                st.dataframe(pending_df, use_container_width=True)
            else:
                st.info("Tidak ada data lamaran yang berstatus pending.")

        show_pending()

    elif btn_detail_lolos:

        @st.dialog("✅ Rincian Lamaran Lolos", width="large")
        def show_lolos():
            if not lolos_df.empty:
                st.dataframe(lolos_df, use_container_width=True)
            else:
                st.info("Tidak ada data lamaran yang berstatus lolos.")

        show_lolos()

    elif btn_detail_gagal:

        @st.dialog("❌ Rincian Lamaran Gagal", width="large")
        def show_gagal():
            if not gagal_df.empty:
                st.dataframe(gagal_df, use_container_width=True)
            else:
                st.info("Tidak ada data lamaran yang berstatus gagal.")

        show_gagal()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # --- BAGIAN FILTER & TABEL UTAMA ---
    st.subheader("📋 Data Keseluruhan Lamaran Kerja")

    fcol1, fcol2, fcol3 = st.columns(3)

    with fcol1:
        search_query = st.text_input(
            "🔍 Cari Perusahaan / Posisi",
            placeholder="Ketik nama...",
        )

    platform_col_all = next(
        (
            c
            for c in df.columns
            if "nemu loker" in c.lower() or "sumber" in c.lower()
        ),
        None,
    )
    with fcol2:
        platforms = (
            ["Semua"] + list(df[platform_col_all].unique())
            if platform_col_all
            else ["Semua"]
        )
        selected_platform = st.selectbox("📌 Filter Sumber Platform", platforms)

    work_type_col = next(
        (c for c in df.columns if "jenis kerja" in c.lower()), None
    )
    with fcol3:
        work_types = (
            ["Semua"] + list(df[work_type_col].unique())
            if work_type_col
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
        and platform_col_all
        and platform_col_all in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df[platform_col_all] == selected_platform
        ]

    if (
        selected_work_type != "Semua"
        and work_type_col
        and work_type_col in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df[work_type_col] == selected_work_type
        ]

    # Hapus kolom helper tampilan agar tidak ikut tampil
    if "Display_Label" in filtered_df.columns:
        filtered_df = filtered_df.drop(columns=["Display_Label"])

    st.dataframe(filtered_df, use_container_width=True)
    st.caption(
        f"Menampilkan {len(filtered_df)} dari total {len(df)} data lamaran."
    )

else:
    st.info(
        "🚀 Belum ada data atau kolom 'Hasil' tidak terbaca di Google Sheets."
    )
