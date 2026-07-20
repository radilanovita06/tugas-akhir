import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import time
from supabase import create_client, Client

# =========================================================
# DATA LOGO (base64, biar tidak perlu upload file gambar terpisah)
# =========================================================


st.set_page_config(
    page_title="Sistem Informasi Realisasi Anggaran (SIRA)",
    page_icon="🏛️",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background: #eaf3fc !important; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f4faff 0%, #e7f1fb 55%, #dbe9f8 100%) !important;
}
.block-container { padding-top: 2rem; max-width: 1450px; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d52 0%, #1d4d80 100%) !important;
    border-right: 3px solid #C8A951;
}
[data-testid="stSidebar"] * { color: #ffffff !important; }
[data-testid="stSidebar"] .user-name { color: #ffffff !important; }
[data-testid="stSidebar"] .user-role { color: #cfe0f5 !important; }
[data-testid="stSidebar"] .user-card {
    background: rgba(255,255,255,.08) !important;
    border: 1px solid rgba(255,255,255,.18) !important;
}
.gov-header {
    background: linear-gradient(135deg, #0f2d52, #1d4d80);
    border-radius: 28px;
    padding: 35px;
    border-left: 8px solid #C8A951;
    box-shadow: 0 20px 40px rgba(15,23,42,.15);
    margin-bottom: 30px;
}
.gov-header-logo-wrap {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 8px;
}
.gov-header-logo-wrap img { height: 34px; }
.gov-header-title {
    color: #ffffff !important;
    font-size: 34px;
    font-weight: 800 !important;
    margin: 0;
    letter-spacing: .2px;
    line-height: 1.3;
}
.gov-header-sub {
    color: #e8f1fd !important;
    margin-top: 10px;
    font-weight: 600 !important;
    font-size: 15px;
}
/* Kotak form (st.form) -- bawaan Streamlit -- dikasih tint biru muda
   supaya nggak nyaru sama background halaman yang terang. */
[data-testid="stForm"] {
    background: #eaf3fc !important;
    border: 2px solid #a9c8ea !important;
    border-radius: 22px !important;
    padding: 28px !important;
}

.card {
    background: #ffffff;
    border-radius: 26px;
    padding: 30px;
    border: 2px solid #bcd9f4;
    box-shadow: 0 14px 34px rgba(15,23,42,.08);
}
.chart-card {
    background: #ffffff;
    border-radius: 22px;
    padding: 22px;
    border: 2px solid #bcd9f4;
    box-shadow: 0 10px 26px rgba(15,23,42,.07);
}
h1, h2, h3, h4, h5, h6, label, p, span { color: #1e293b !important; }
/* SEMUA kolom input (teks, angka, textarea, tanggal, dropdown, multiselect)
   diberi warna isi PENUH (bukan cuma border) supaya konsisten di seluruh
   halaman -- fill biru muda dengan teks biru gelap tebal biar tetap
   jelas dibaca. */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stDateInput input,
.stSelectbox div[data-baseweb="select"],
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] > div {
    background-color: #dbeafe !important;
    color: #0f2d52 !important;
    border-radius: 14px !important;
    border: 1.5px solid #93c5fd !important;
    font-weight: 600 !important;
}
.stSelectbox div[data-baseweb="select"] *,
.stMultiSelect div[data-baseweb="select"] * { color: #0f2d52 !important; }

/* Placeholder teks di kolom input/search supaya tetap kebaca */
.stTextInput input::placeholder,
.stNumberInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #5b7ca8 !important;
    opacity: 1 !important;
}

/* Chip/tag hasil pilihan di multiselect (Filter Unit, Filter Bulan, dsb)
   dibuat biru muda netral, bukan merah -- supaya tidak berkesan
   "peringatan/bahaya" padahal cuma menunjukkan filter aktif. */
[data-baseweb="tag"] {
    background-color: #dbeafe !important;
    border: 1px solid #93c5fd !important;
}
[data-baseweb="tag"] span { color: #1e3a8a !important; }
[data-baseweb="tag"] svg { fill: #1e3a8a !important; }

/* Tombol aksi utama (Simpan, Masuk, Upload, dsb) = NAVY BIRU,
   disamakan dengan warna sidebar. Teks putih tegas biar kebaca jelas.
   Pakai wildcard (*) supaya kena semua elemen anak di dalam tombol,
   apapun tag-nya -- karena target tag spesifik (p/span/div) ternyata
   tidak selalu cocok dengan struktur HTML tombol Streamlit. */
.stButton button,
.stFormSubmitButton button {
    background: linear-gradient(135deg, #0f2d52, #1d4d80) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 18px rgba(15,45,82,.28);
}
.stButton button *,
.stFormSubmitButton button * {
    color: #ffffff !important;
    fill: #ffffff !important;
}
/* Tombol download = KUNING/EMAS (aksen brand) */
.stDownloadButton button {
    background: linear-gradient(135deg, #C8A951, #d8bc6b) !important;
    color: #1e293b !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
}
.stDownloadButton button * {
    color: #1e293b !important;
    fill: #1e293b !important;
}
/* Tombol destruktif (type="primary", dipakai untuk Hapus Data) = MAROON */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #6b1414, #8f1d1d) !important;
    color: #ffffff !important;
    box-shadow: 0 8px 18px rgba(107,20,20,.3);
}
.stButton button[kind="primary"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
}
/* Tombol Logout di sidebar = MAROON */
[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, #6b1414, #8f1d1d) !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stButton button * {
    color: #ffffff !important;
    fill: #ffffff !important;
}
/* Tombol Refresh Data = BIRU (bukan hijau, biar beda dari aksi simpan) */
.st-key-refresh_btn_lihat_semua .stButton button,
.st-key-refresh_btn_kelola_data .stButton button {
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    color: #ffffff !important;
    box-shadow: 0 8px 18px rgba(37,99,235,.25);
}
.st-key-refresh_btn_lihat_semua .stButton button *,
.st-key-refresh_btn_kelola_data .stButton button * {
    color: #ffffff !important;
    fill: #ffffff !important;
}
.metric-card {
    background: #ffffff;
    border-radius: 22px;
    padding: 24px;
    border: 1.5px solid #bcd9f4;
    border-left: 6px solid #C8A951;
    box-shadow: 0 10px 26px rgba(15,23,42,.07);
    margin-bottom: 16px;
}
.metric-card.metric-good { border-left-color: #16a34a; }
.metric-card.metric-warning { border-left-color: #f59e0b; }
.metric-card.metric-danger { border-left-color: #dc2626; }
.metric-title { color: #64748b !important; font-size: 14px; }
.metric-value {
    color: #0f172a !important;
    font-size: clamp(18px, 2.1vw, 25px);
    font-weight: 800;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
[data-testid="stDataFrame"],
[data-testid="stDataEditor"] {
    border-radius: 18px;
    overflow: hidden;
    border: 2px solid #1d4d80;
}
/* Tabel ringkasan custom (Ringkasan per Unit, Ringkasan Bulanan) --
   st.dataframe dirender pakai canvas jadi warnanya tidak bisa diubah
   lewat CSS, makanya tabel-tabel ringkasan itu dibikin manual pakai
   HTML supaya headernya bisa disamakan dengan warna tombol Download
   (emas), teks putih. */
.custom-table-wrap {
    overflow-x: auto;
    overflow-y: auto;
    max-height: 520px;
    border-radius: 18px;
    border: 1.5px solid #bcd9f4;
    background: #ffffff;
}
.custom-table { width: 100%; border-collapse: collapse; }
.custom-table thead th {
    background: linear-gradient(135deg, #C8A951, #d8bc6b) !important;
    color: #ffffff !important;
    padding: 12px 16px;
    text-align: left;
    font-weight: 700;
    white-space: nowrap;
    position: sticky;
    top: 0;
    z-index: 1;
}
.custom-table tbody td {
    padding: 10px 16px;
    color: #1e293b !important;
    border-bottom: 1px solid #e6eaf1;
}
.custom-table tbody tr:nth-child(even) { background: #f4f9ff; }
.custom-table tbody tr:hover { background: #eaf3fc; }
.login-wrap { max-width: 460px; margin: 7vh auto 0 auto; }
.login-logo {
    display: flex; align-items: center; justify-content: center;
    gap: 10px; margin: 0 auto 18px auto;
}
.login-logo img { height: 56px; }
.login-title { text-align: center; font-size: 30px; font-weight: 800; color: #0f172a !important; }
.login-subtitle { text-align: center; color: #64748b !important; margin-bottom: 28px; }
.app-copyright {
    position: fixed;
    bottom: 10px;
    right: 16px;
    font-size: 12px;
    color: #94a3b8 !important;
    background: rgba(255,255,255,.85);
    padding: 4px 10px;
    border-radius: 8px;
    z-index: 999;
    pointer-events: none;
}
.user-card {
    background: #f8fafc;
    border: 1px solid #cfe3f7;
    border-radius: 16px; padding: 14px; margin: 10px 0 18px 0;
}
.user-name { font-weight: 800; color: #0f172a !important; }
.user-role { font-size: 12px; color: #64748b !important; }
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="app-copyright">© 2026 RDN-UNJ</div>',
    unsafe_allow_html=True
)

# =========================================================
# KONEKSI SUPABASE
# Isi kredensial ini lewat .streamlit/secrets.toml (lokal) atau
# menu Settings > Secrets di Streamlit Cloud, JANGAN ditulis
# langsung di kode. Formatnya:
#
# [supabase]
# url = "https://xxxxx.supabase.co"
# key = "xxxxxxxxxxxxxxxxxxxxxxx"
#
# Skema tabel yang dipakai (jalankan sekali di SQL Editor Supabase):
#
# create table anggaran (
#     id bigint generated always as identity primary key,
#     unit text not null,
#     tanggal text not null,
#     mak text not null,
#     kegiatan text not null,
#     pagu numeric not null default 0,
#     realisasi numeric not null default 0,
#     created_at timestamptz not null default now()
# );
#
# alter table anggaran enable row level security;
#
# -- Karena login diatur sendiri di aplikasi (bukan lewat Supabase Auth)
# -- dan aplikasi memakai service_role key di server Streamlit,
# -- policy publik tidak wajib dibuka. Kalau tetap ingin
# -- mengaktifkan akses lewat anon key, tambahkan policy berikut:
# -- create policy "allow all" on anggaran for all using (true) with check (true);
# =========================================================

TABLE_NAME = "anggaran"


@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


supabase = get_supabase_client()

# =========================================================
# AKUN LOGIN
# Ganti username/password di sini.
# Untuk produksi, simpan password di database atau st.secrets.
# =========================================================
USERS = {
    "admin": {
        "password": "admin123",
        "name": "Administrator",
        "role": "Admin"
    },
    "operator": {
        "password": "operator123",
        "name": "Operator Anggaran",
        "role": "Operator"
    }
}

UNIT_LIST = ["Sekretariat", "IHHP", "IMHLP", "MINTEMGAR", "IKOP", "DIREKTIF"]

# Warna tetap per Unit -- dipakai KONSISTEN di semua grafik supaya
# satu unit selalu punya warna yang sama di mana pun ditampilkan.
# Palet dipilih supaya masih senada dengan tema biru-navy-emas situs,
# tapi tetap kontras/beda satu sama lain.
UNIT_COLORS = {
    "Sekretariat": "#16a34a",   # hijau
    "IHHP": "#1d4d80",          # navy
    "IMHLP": "#C8A951",         # emas
    "MINTEMGAR": "#0891b2",     # teal
    "IKOP": "#7c3aed",          # ungu
    "DIREKTIF": "#dc2626",      # merah
}
UNIT_COLOR_RANGE = [UNIT_COLORS[u] for u in UNIT_LIST]


def chart_header(title: str):
    """Judul grafik ditampilkan di LUAR gambar chart (bukan title bawaan
    Altair), supaya gayanya konsisten dengan header lain di halaman ini."""
    st.markdown(
        f'<div style="font-weight:700;font-size:16px;color:#0f2d52;margin-bottom:6px;">{title}</div>',
        unsafe_allow_html=True
    )

BULAN_LIST = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

# Kolom yang tampil di UI (tanpa "id", karena id cuma dipakai internal)
TEMPLATE_COLUMNS = [
    "Unit",
    "Tanggal",
    "No",
    "MAK",
    "Kegiatan",
    "Pagu",
    "Realisasi",
    "Sisa Anggaran"
]

# Mapping nama kolom UI <-> nama kolom tabel Supabase
DB_COLUMN_MAP = {
    "Unit": "unit",
    "Tanggal": "tanggal",
    "MAK": "mak",
    "Kegiatan": "kegiatan",
    "Pagu": "pagu",
    "Realisasi": "realisasi",
}


def init_state():
    defaults = {
        "authenticated": False,
        "current_user": None,
        "edit_index": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


def login_user(username: str, password: str) -> bool:
    user = USERS.get(username.strip())
    if user and user["password"] == password:
        st.session_state.authenticated = True
        st.session_state.current_user = {
            "username": username.strip(),
            "name": user["name"],
            "role": user["role"]
        }
        return True
    return False


def logout_user():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.edit_index = None
    st.rerun()


def is_admin() -> bool:
    return (
        st.session_state.current_user is not None
        and st.session_state.current_user.get("role") == "Admin"
    )


def clean_money(value):
    if pd.isna(value) or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = (
        str(value)
        .replace("Rp", "")
        .replace("rp", "")
        .replace(" ", "")
        .replace(".", "")
        .replace(",", ".")
    )
    result = pd.to_numeric(cleaned, errors="coerce")
    return 0.0 if pd.isna(result) else float(result)


def format_rupiah(value):
    try:
        return f"Rp{float(value):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "Rp0"


def rupiah_axis(title: str):
    """Axis grafik dalam format Rupiah penuh, tanpa singkatan G/K/M."""
    return alt.Axis(
        title=title,
        labelExpr="'Rp ' + replace(format(datum.value, ',.0f'), ',', '.')",
        labelLimit=180
    )


def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Rapikan nama kolom agar tahan terhadap spasi, kapital, dan typo umum."""
    df = df.copy()

    aliases = {
        "unit": "Unit",
        "direktorat": "Unit",
        "penanggung jawab": "Unit",
        "tanggal": "Tanggal",
        "date": "Tanggal",
        "no": "No",
        "nomor": "No",
        "mak": "MAK",
        "kegiatan": "Kegiatan",
        "pagu": "Pagu",
        "realisasi": "Realisasi",
        "realosaso": "Realisasi",
        "sisa anggaran": "Sisa Anggaran",
        "sisa amggaran": "Sisa Anggaran",
    }

    renamed = {}
    for col in df.columns:
        cleaned = " ".join(str(col).replace("\ufeff", "").strip().split()).lower()
        renamed[col] = aliases.get(cleaned, str(col).strip())

    return df.rename(columns=renamed)


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        # sep=None + python engine mendeteksi koma, titik koma, atau tab otomatis.
        return pd.read_csv(uploaded_file, sep=None, engine="python", encoding="utf-8-sig")

    try:
        return pd.read_excel(uploaded_file, engine="calamine")
    except (ImportError, ModuleNotFoundError) as exc:
        raise RuntimeError(
            "Mesin pembaca Excel belum terpasang. Pastikan requirements.txt berisi "
            "python-calamine dan pandas>=2.2.0."
        ) from exc


def normalize_bulan(value):
    """Baca nama bulan tanpa tanggal/tahun, termasuk singkatan dan angka 1-12."""
    if pd.isna(value) or str(value).strip() == "":
        return ""

    text = str(value).strip().lower()
    aliases = {
        "1": "Januari", "01": "Januari", "jan": "Januari", "januari": "Januari",
        "2": "Februari", "02": "Februari", "feb": "Februari", "februari": "Februari",
        "3": "Maret", "03": "Maret", "mar": "Maret", "maret": "Maret",
        "4": "April", "04": "April", "apr": "April", "april": "April",
        "5": "Mei", "05": "Mei", "may": "Mei", "mei": "Mei",
        "6": "Juni", "06": "Juni", "jun": "Juni", "juni": "Juni",
        "7": "Juli", "07": "Juli", "jul": "Juli", "juli": "Juli",
        "8": "Agustus", "08": "Agustus", "agu": "Agustus", "aug": "Agustus", "agustus": "Agustus",
        "9": "September", "09": "September", "sep": "September", "september": "September",
        "10": "Oktober", "okt": "Oktober", "oct": "Oktober", "oktober": "Oktober",
        "11": "November", "nov": "November", "november": "November",
        "12": "Desember", "des": "Desember", "dec": "Desember", "desember": "Desember",
    }

    if text in aliases:
        return aliases[text]

    # Tetap bisa membaca jika Excel menyimpan tanggal lengkap.
    parsed = pd.to_datetime(value, errors="coerce", dayfirst=True)
    if not pd.isna(parsed):
        return BULAN_LIST[parsed.month - 1]

    return str(value).strip().title()


def normalize_data(df: pd.DataFrame, keep_id: bool = False) -> pd.DataFrame:
    df = normalize_headers(df)

    for col in TEMPLATE_COLUMNS:
        if col not in df.columns:
            df[col] = "" if col in ["Unit", "Tanggal", "MAK", "Kegiatan"] else 0

    columns_to_use = (["id"] + TEMPLATE_COLUMNS) if (keep_id and "id" in df.columns) else TEMPLATE_COLUMNS
    df = df[columns_to_use]
    df["Unit"] = df["Unit"].fillna("").astype(str).str.strip()
    df["Tanggal"] = df["Tanggal"].apply(normalize_bulan)
    df["MAK"] = df["MAK"].fillna("").astype(str).str.strip()
    df["Kegiatan"] = df["Kegiatan"].fillna("").astype(str).str.strip()
    df["Pagu"] = df["Pagu"].apply(clean_money)
    df["Realisasi"] = df["Realisasi"].apply(clean_money)
    df["Sisa Anggaran"] = df["Pagu"] - df["Realisasi"]
    df = df.reset_index(drop=True)
    df["No"] = range(1, len(df) + 1)
    return df


def get_latest_snapshot(df: pd.DataFrame) -> pd.DataFrame:
    """Pagu dan Realisasi yang diupload tiap bulan sifatnya SNAPSHOT:
    Pagu = plafon anggaran terkini (bisa berubah karena revisi/operan
    antar kegiatan), Realisasi = akumulasi realisasi SAMPAI DENGAN bulan
    tersebut (bukan realisasi khusus bulan itu saja). Karena keduanya
    snapshot, keduanya TIDAK BOLEH dijumlah lintas bulan untuk kegiatan
    yang sama, atau angkanya akan dobel/berlipat.

    Fungsi ini mengambil SATU baris per kegiatan (Unit+MAK), yaitu entri
    dari bulan PALING AKHIR yang tersedia pada rentang data/filter yang
    dipilih, supaya total Pagu maupun Realisasi mencerminkan kondisi
    terkini kegiatan tersebut, bukan hasil penjumlahan berulang.

    Baris dengan Pagu = 0 dianggap "belum diisi" (mis. bulan yang memang
    belum sempat di-upload/masih placeholder kosong pada template),
    BUKAN snapshot sungguhan. Kalau bulan terakhir yang ADA di data
    ternyata masih 0, itu tidak boleh menimpa data valid dari bulan
    sebelumnya -- jadi snapshot diambil dari bulan paling akhir yang
    Pagu-nya sudah benar-benar diisi (> 0). Kalau suatu kegiatan memang
    belum pernah diisi sama sekali, baru dipakai baris terakhirnya
    apa adanya (termasuk yang masih 0)."""
    if df.empty:
        return pd.DataFrame(columns=["Unit", "MAK", "Kegiatan", "Tanggal", "Pagu", "Realisasi"])

    temp = df.copy()
    temp["Urutan Bulan"] = temp["Tanggal"].apply(
        lambda x: BULAN_LIST.index(x) if x in BULAN_LIST else -1
    )
    temp = temp.sort_values("Urutan Bulan")

    filled = temp[temp["Pagu"] > 0]
    filled_latest = filled.drop_duplicates(subset=["Unit", "MAK"], keep="last")

    all_latest = temp.drop_duplicates(subset=["Unit", "MAK"], keep="last")
    filled_keys = set(zip(filled_latest["Unit"], filled_latest["MAK"]))
    missing_latest = all_latest[
        ~all_latest.apply(lambda row: (row["Unit"], row["MAK"]) in filled_keys, axis=1)
    ]

    result = pd.concat([filled_latest, missing_latest], ignore_index=True)
    return (
        result[["Unit", "MAK", "Kegiatan", "Tanggal", "Pagu", "Realisasi"]]
        .reset_index(drop=True)
    )


def render_summary_table(df: pd.DataFrame):
    """st.dataframe di Streamlit versi baru dirender pakai canvas, jadi
    warna header-nya TIDAK BISA diubah lewat CSS sama sekali. Untuk tabel
    ringkasan yang statis (bukan tabel besar yang perlu sortir/scroll),
    kita bikin tabel HTML manual supaya warna headernya bisa dikontrol
    penuh -- disamakan dengan warna tombol Download (emas), teks putih."""
    headers_html = "".join(f"<th>{col}</th>" for col in df.columns)
    rows_html = ""
    for _, row in df.iterrows():
        cells = "".join(f"<td>{row[col]}</td>" for col in df.columns)
        rows_html += f"<tr>{cells}</tr>"
    st.markdown(f"""
    <div class="custom-table-wrap">
    <table class="custom-table">
        <thead><tr>{headers_html}</tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)


def display_data(df: pd.DataFrame) -> pd.DataFrame:
    result = normalize_data(df)
    for col in ["Pagu", "Realisasi", "Sisa Anggaran"]:
        result[col] = result[col].apply(format_rupiah)
    return result


def to_csv(df: pd.DataFrame):
    return df.to_csv(index=False).encode("utf-8-sig")


def to_xlsx(df: pd.DataFrame):
    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Data Anggaran")
        return output.getvalue()
    except ModuleNotFoundError as exc:
        st.error("XlsxWriter belum terpasang. Template CSV tetap bisa dipakai.")
        st.code("pip install XlsxWriter")
        return None


# =========================================================
# FUNGSI AKSES DATA KE SUPABASE
# =========================================================
def fetch_data() -> pd.DataFrame:
    """Ambil seluruh data dari tabel Supabase dan ubah ke format kolom UI."""
    try:
        response = supabase.table(TABLE_NAME).select("*").order("id").execute()
    except Exception as exc:
        st.error(f"Gagal mengambil data dari Supabase: {exc}")
        return pd.DataFrame(columns=["id"] + TEMPLATE_COLUMNS)

    rows = response.data or []
    if not rows:
        return pd.DataFrame(columns=["id"] + TEMPLATE_COLUMNS)

    df = pd.DataFrame(rows)
    reverse_map = {v: k for k, v in DB_COLUMN_MAP.items()}
    df = df.rename(columns=reverse_map)
    df = normalize_data(df, keep_id=True)
    return df


def insert_row(unit, tanggal, mak, kegiatan, pagu, realisasi):
    """Upsert satu baris: kalau Unit+Tanggal+MAK sudah ada, nilainya DIGANTI
    dengan angka baru (bukan dijumlahkan). Kalau belum ada, jadi baris baru."""
    payload = {
        "unit": unit,
        "tanggal": tanggal,
        "mak": mak,
        "kegiatan": kegiatan,
        "pagu": float(pagu),
        "realisasi": float(realisasi),
    }
    supabase.table(TABLE_NAME).upsert(
        payload, on_conflict="unit,tanggal,mak"
    ).execute()


def insert_bulk(df: pd.DataFrame):
    """Upsert banyak baris sekaligus (dipakai saat Upload Template).
    Baris dengan Unit+Tanggal+MAK yang sama dengan data lama akan
    DIGANTI nilainya (Pagu/Realisasi jadi angka terbaru dari file),
    bukan ditambahkan sebagai baris baru sehingga tidak dobel hitung.

    Kalau file yang diupload sendiri punya baris DOBEL untuk kombinasi
    Unit+Tanggal+MAK yang sama, Postgres akan menolak (error 21000:
    "ON CONFLICT DO UPDATE command cannot affect row a second time")
    karena tidak bisa update baris yang sama dua kali dalam satu
    perintah. Makanya di sini dibersihkan dulu -- kalau ada duplikat,
    yang dipakai baris yang PALING TERAKHIR muncul di file."""
    df = df.drop_duplicates(subset=["Unit", "Tanggal", "MAK"], keep="last")
    records = df.rename(columns=DB_COLUMN_MAP)[list(DB_COLUMN_MAP.values())].to_dict("records")
    if records:
        supabase.table(TABLE_NAME).upsert(
            records, on_conflict="unit,tanggal,mak"
        ).execute()


def update_row(row_id, unit, tanggal, mak, kegiatan, pagu, realisasi):
    payload = {
        "unit": unit,
        "tanggal": tanggal,
        "mak": mak,
        "kegiatan": kegiatan,
        "pagu": float(pagu),
        "realisasi": float(realisasi),
    }
    supabase.table(TABLE_NAME).update(payload).eq("id", int(row_id)).execute()


def update_rows_bulk(df: pd.DataFrame):
    """Simpan banyak perubahan sekaligus dalam SATU request ke Supabase
    (bukan satu request per baris seperti update_row di atas). Jauh lebih
    cepat kalau tabel yang diedit isinya puluhan/ratusan baris, karena
    tidak perlu bolak-balik ke server untuk tiap baris satu per satu."""
    records = df.rename(columns=DB_COLUMN_MAP)[["id"] + list(DB_COLUMN_MAP.values())].to_dict("records")
    if records:
        supabase.table(TABLE_NAME).upsert(records, on_conflict="id").execute()


def delete_rows(ids):
    ids = [int(i) for i in ids]
    if ids:
        supabase.table(TABLE_NAME).delete().in_("id", ids).execute()


def show_login():
    st.markdown("""
    <div class="login-wrap">
        <div class="login-logo"><img src="data:image/png;base64,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" /><img src="data:image/png;base64,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" /></div>
        <div class="login-title">Sistem Informasi Realisasi Anggaran (SIRA)</div>
        <div class="login-subtitle">Masuk untuk mengakses dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.15, 1])
    with center:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Masuk", use_container_width=True)

        if submitted:
            if login_user(username, password):
                st.rerun()
            else:
                st.error("Username atau password salah")


if not st.session_state.authenticated:
    show_login()
    st.stop()

current_user = st.session_state.current_user

st.sidebar.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
    <img src="data:image/png;base64,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" style="height:56px;" />
    <img src="data:image/png;base64,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" style="height:56px;" />
</div>
""", unsafe_allow_html=True)

st.sidebar.title("Menu Sistem")
st.sidebar.caption("Versi aplikasi: 2026.07.15-v6-supabase")
st.sidebar.markdown(f"""
<div class="user-card">
    <div class="user-name">{current_user['name']}</div>
    <div class="user-role">{current_user['role']}</div>
</div>
""", unsafe_allow_html=True)

menu_items = [
    "Dashboard",
    "Input Data",
    "Upload Template",
    "Lihat Semua Data"
]
if is_admin():
    menu_items.append("Kelola Data")

menu = st.sidebar.radio("Pilih Menu", menu_items)

if st.sidebar.button("Logout", use_container_width=True):
    logout_user()

st.markdown("""
<div class="gov-header">
    <div class="gov-header-logo-wrap"><img src="data:image/png;base64,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" /><img src="data:image/png;base64,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" /></div>
    <div class="gov-header-title" style="color:#ffffff !important;">Sistem Informasi Realisasi Anggaran (SIRA)</div>
    <div class="gov-header-sub" style="color:#e8f1fd !important;">Monitoring Pagu, Realisasi, dan Sisa Anggaran</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# DASHBOARD - HALAMAN AWAL SETELAH LOGIN
# =========================================================
if menu == "Dashboard":
    st.subheader(f"Selamat datang, {current_user['name']} 👋")
    st.caption("Ringkasan kondisi anggaran terkini di seluruh unit.")

    df_dashboard = fetch_data()

    if df_dashboard.empty:
        st.info("Belum ada data anggaran. Silakan input atau upload data terlebih dahulu.")
    else:
        # Ringkasan dashboard dihitung dari SELURUH data (semua unit,
        # tanpa filter), menggunakan snapshot bulan terakhir per
        # kegiatan -- sama seperti logika di halaman Lihat Semua Data.
        dash_snapshot = get_latest_snapshot(df_dashboard)
        dash_total_pagu = dash_snapshot["Pagu"].sum()
        dash_total_realisasi = dash_snapshot["Realisasi"].sum()
        dash_total_sisa = dash_total_pagu - dash_total_realisasi
        dash_serapan = (dash_total_realisasi / dash_total_pagu * 100) if dash_total_pagu > 0 else 0

        if dash_serapan < 40:
            dash_serapan_class = "metric-danger"
        elif dash_serapan < 75:
            dash_serapan_class = "metric-warning"
        else:
            dash_serapan_class = "metric-good"

        d1, d2 = st.columns(2)
        d3, d4 = st.columns(2)
        dash_metric_items = [
            (d1, "Total Pagu", format_rupiah(dash_total_pagu), ""),
            (d2, "Total Realisasi", format_rupiah(dash_total_realisasi), "metric-good"),
            (d3, "Sisa Anggaran", format_rupiah(dash_total_sisa), ""),
            (d4, "Serapan Anggaran", f"{dash_serapan:.2f}%".replace(".", ","), dash_serapan_class),
        ]
        for column, title, value, extra_class in dash_metric_items:
            with column:
                st.markdown(f"""
                <div class="metric-card {extra_class}">
                    <div class="metric-title">{title}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """, unsafe_allow_html=True)

        st.caption("Detail per unit, filter, dan grafik lengkap ada di menu \"Lihat Semua Data\".")

# =========================================================
# INPUT DATA - ADMIN DAN OPERATOR
# =========================================================
elif menu == "Input Data":
    st.subheader("Input Data Anggaran")

    # Reset kolom form setelah berhasil simpan (dilakukan SEBELUM widget
    # dibuat, karena Streamlit tidak izinkan ubah session_state widget
    # sesudah widget itu dirender di run yang sama).
    if st.session_state.get("_reset_input_form"):
        st.session_state["input_mak"] = ""
        st.session_state["input_kegiatan"] = ""
        st.session_state["input_pagu"] = 0
        st.session_state["input_realisasi"] = 0
        st.session_state["_reset_input_form"] = False

    col1, col2 = st.columns(2)
    with col1:
        unit = st.selectbox("Unit", UNIT_LIST, key="input_unit")
        tanggal = st.selectbox("Tanggal (Bulan)", BULAN_LIST, key="input_tanggal")
        mak = st.text_input("MAK", placeholder="Contoh: 521211", key="input_mak")
        kegiatan = st.text_area("Kegiatan", key="input_kegiatan")
    with col2:
        pagu = st.number_input("Pagu (Rp)", min_value=0, step=1_000_000, key="input_pagu")
        st.caption(f"= {format_rupiah(pagu)}")
        realisasi = st.number_input("Realisasi (Rp)", min_value=0, step=1_000_000, key="input_realisasi")
        st.caption(f"= {format_rupiah(realisasi)}")
        sisa = pagu - realisasi
        st.info(f"Sisa Anggaran: {format_rupiah(sisa)}")

    if st.button("Simpan Data", use_container_width=True):
        if not mak.strip() or not kegiatan.strip():
            st.error("MAK dan Kegiatan wajib diisi")
        else:
            try:
                insert_row(unit, tanggal, mak.strip(), kegiatan.strip(), pagu, realisasi)
                st.success("Data berhasil disimpan ke Supabase")
                st.session_state["_reset_input_form"] = True
                st.rerun()
            except Exception as exc:
                st.error(f"Gagal menyimpan data: {exc}")


# =========================================================
# UPLOAD - ADMIN DAN OPERATOR
# =========================================================
elif menu == "Upload Template":
    st.subheader("Upload Data Menggunakan Template")

    template = pd.DataFrame(columns=TEMPLATE_COLUMNS)
    template["Tanggal"] = pd.Series(dtype="object")

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Download Template CSV",
            data=to_csv(template),
            file_name="Template_Monitoring_Anggaran.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c2:
        xlsx_template = to_xlsx(template)
        if xlsx_template is not None:
            st.download_button(
                "Download Template XLSX",
                data=xlsx_template,
                file_name="Template_Monitoring_Anggaran.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    selected_unit = st.selectbox(
        "Pilih Unit Data",
        UNIT_LIST,
        help="Semua baris dari file yang di-upload akan otomatis masuk ke unit ini."
    )

    uploaded_file = st.file_uploader("Upload CSV atau XLSX", type=["csv", "xlsx", "xls", "xlsm", "xlsb"])

    if uploaded_file is not None:
        try:
            upload_df = read_uploaded_file(uploaded_file)
            upload_df = normalize_headers(upload_df)

            required = ["Tanggal", "MAK", "Kegiatan", "Pagu", "Realisasi"]
            missing = [col for col in required if col not in upload_df.columns]

            if missing:
                detected = ", ".join(map(str, upload_df.columns.tolist())) or "tidak ada kolom"
                st.error(f"Kolom wajib belum ada: {', '.join(missing)}")
                st.caption(f"Kolom yang terbaca: {detected}")
                st.info(
                    "Gunakan header: Tanggal, No, MAK, Kegiatan, Pagu, Realisasi, Sisa Anggaran. Kolom Unit tidak wajib karena otomatis mengikuti pilihan di atas."
                )
            else:
                upload_df["Unit"] = selected_unit
                upload_df = normalize_data(upload_df)
                st.subheader("Preview")
                render_summary_table(display_data(upload_df))

                if st.button("Simpan Data Upload", use_container_width=True):
                    progress = st.progress(0, text="Menyiapkan data...")

                    for value, message in [
                        (25, "Memeriksa format file..."),
                        (55, "Menghitung sisa anggaran..."),
                        (80, "Menyimpan data ke Supabase..."),
                        (100, "Upload selesai")
                    ]:
                        time.sleep(0.20)
                        progress.progress(value, text=message)

                    try:
                        jumlah_sebelum = len(upload_df)
                        upload_df_bersih = upload_df.drop_duplicates(
                            subset=["Unit", "Tanggal", "MAK"], keep="last"
                        )
                        jumlah_duplikat = jumlah_sebelum - len(upload_df_bersih)

                        # Cari baris mana saja yang kombinasi Unit+Tanggal+MAK-nya
                        # muncul lebih dari 1x di file ini, supaya bisa ditunjukkan
                        # detailnya ke pengguna (bukan cuma jumlahnya doang).
                        if jumlah_duplikat > 0:
                            mask_duplikat = upload_df.duplicated(
                                subset=["Unit", "Tanggal", "MAK"], keep=False
                            )
                            baris_duplikat = upload_df[mask_duplikat].sort_values(
                                ["Unit", "Tanggal", "MAK"]
                            )

                        insert_bulk(upload_df)
                        st.toast("Upload sukses, data udah masuk 😹", icon="✅")
                        st.success(
                            f"Upload berhasil. {len(upload_df_bersih)} baris data udah disimpan ke Supabase."
                        )
                        if jumlah_duplikat > 0:
                            st.warning(
                                f"Ditemukan {jumlah_duplikat} baris dengan kombinasi Unit+Bulan+MAK yang "
                                "sama persis di dalam file ini. Yang dipakai adalah baris paling terakhir "
                                "untuk tiap kombinasi tersebut. Berikut baris-baris yang dobel:"
                            )
                            render_summary_table(display_data(baris_duplikat))
                        st.balloons()
                    except Exception as exc:
                        st.error(f"Gagal menyimpan data ke Supabase: {exc}")

        except Exception as exc:
            st.error(f"File gagal dibaca: {exc}")


# =========================================================
# LIHAT DATA - ADMIN DAN OPERATOR
# =========================================================
elif menu == "Lihat Semua Data":
    st.subheader("Monitoring Data Anggaran")

    with st.container(key="refresh_btn_lihat_semua"):
        if st.button("🔄 Refresh Data"):
            st.rerun()

    df_raw = fetch_data()

    if df_raw.empty:
        st.warning("Belum ada data")
    else:
        df = df_raw.drop(columns=["id"])

        filter0, filter1, filter2, filter3 = st.columns([1.1, 1.2, 1.2, 1.6])
        with filter0:
            selected_units = st.multiselect(
                "Filter Unit",
                UNIT_LIST,
                default=[u for u in UNIT_LIST if u in df["Unit"].unique()]
            )
        with filter1:
            selected_months = st.multiselect(
                "Filter Bulan",
                BULAN_LIST,
                default=[m for m in BULAN_LIST if m in df["Tanggal"].unique()]
            )
        with filter2:
            search_mak = st.text_input("Cari MAK", placeholder="Cari kode MAK...")
        with filter3:
            search_kegiatan = st.text_input("Cari Kegiatan", placeholder="Cari nama kegiatan...")

        filtered = df.copy()
        if selected_units:
            filtered = filtered[filtered["Unit"].isin(selected_units)]
        if selected_months:
            filtered = filtered[filtered["Tanggal"].isin(selected_months)]
        if search_mak:
            filtered = filtered[
                filtered["MAK"].str.contains(search_mak, case=False, na=False)
            ]
        if search_kegiatan:
            filtered = filtered[
                filtered["Kegiatan"].str.contains(search_kegiatan, case=False, na=False)
            ]

        # Pagu maupun Realisasi diambil dari snapshot bulan PALING AKHIR
        # per kegiatan (Unit+MAK), bukan dijumlah lintas bulan — karena
        # keduanya angka "posisi terkini/kumulatif", bukan nilai per bulan
        # yang berdiri sendiri. (total_pagu dipakai di bawah untuk
        # menghitung Sisa Anggaran & Serapan per bulan; kartu ringkasan
        # totalnya sendiri sekarang ditampilkan di halaman Dashboard.)
        latest_snapshot = get_latest_snapshot(filtered)
        total_pagu = latest_snapshot["Pagu"].sum()
        total_realisasi = latest_snapshot["Realisasi"].sum()
        total_sisa = total_pagu - total_realisasi
        serapan = (total_realisasi / total_pagu * 100) if total_pagu > 0 else 0

        st.divider()

        # Di dalam SATU bulan, menjumlahkan Pagu/Realisasi antar KEGIATAN
        # yang berbeda tetap valid (bukan dobel hitung) — karena tiap
        # kegiatan cuma muncul sekali untuk bulan itu. Realisasi di baris
        # tersebut memang sudah kumulatif sampai dengan bulan itu, jadi
        # hasil penjumlahannya otomatis sudah jadi "total realisasi
        # organisasi s.d. bulan tersebut", tanpa perlu trik tambahan.
        month_summary = (
            filtered.groupby("Tanggal", as_index=False)[["Pagu", "Realisasi", "Sisa Anggaran"]]
            .sum()
        )
        month_summary["Urutan Bulan"] = month_summary["Tanggal"].apply(
            lambda x: BULAN_LIST.index(x) if x in BULAN_LIST else 99
        )
        month_summary = month_summary.sort_values("Urutan Bulan")
        month_summary["Serapan"] = month_summary.apply(
            lambda row: (row["Realisasi"] / row["Pagu"] * 100) if row["Pagu"] > 0 else 0,
            axis=1
        )

        if month_summary.empty:
            st.warning("Data tidak ditemukan dari filter yang dipilih")
        else:
            st.subheader("Visualisasi Anggaran")

            g1, g2 = st.columns(2)

            with g1:
                area = (
                    alt.Chart(month_summary)
                    .mark_area(
                        line={"color": "#E8C96A", "strokeWidth": 3},
                        color=alt.Gradient(
                            gradient="linear",
                            stops=[
                                alt.GradientStop(color="#E8C96A", offset=0),
                                alt.GradientStop(color="#214D7D", offset=1),
                            ],
                            x1=1,
                            x2=1,
                            y1=1,
                            y2=0,
                        ),
                        opacity=0.75
                    )
                    .encode(
                        x=alt.X("Tanggal:N", sort=BULAN_LIST, title=None),
                        y=alt.Y("Realisasi:Q", title="Realisasi", axis=rupiah_axis("Realisasi")),
                        tooltip=[
                            alt.Tooltip("Tanggal:N", title="Bulan"),
                            alt.Tooltip("Realisasi Rupiah:N", title="Realisasi")
                        ]
                    )
                    .properties(height=330)
                )
                chart_header("Tren Realisasi per Bulan")
                st.altair_chart(
                    area.configure_axis(labelColor="#375073", titleColor="#375073", gridColor="#dbe9f8")
                        .configure_view(strokeWidth=0),
                    use_container_width=True
                )

            with g2:
                long_month = month_summary.melt(
                    id_vars=["Tanggal"],
                    value_vars=["Pagu", "Realisasi"],
                    var_name="Jenis",
                    value_name="Nilai"
                )
                long_month["Nilai Rupiah"] = long_month["Nilai"].apply(format_rupiah)
                grouped_bar = (
                    alt.Chart(long_month)
                    .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
                    .encode(
                        x=alt.X("Tanggal:N", sort=BULAN_LIST, title=None),
                        xOffset="Jenis:N",
                        y=alt.Y("Nilai:Q", title="Nilai Anggaran", axis=rupiah_axis("Nilai Anggaran")),
                        color=alt.Color(
                            "Jenis:N",
                            scale=alt.Scale(domain=["Pagu", "Realisasi"], range=["#4F86C6", "#E8C96A"]),
                            legend=alt.Legend(title=None, orient="top")
                        ),
                        tooltip=[
                            alt.Tooltip("Tanggal:N", title="Bulan"),
                            alt.Tooltip("Jenis:N", title="Kategori"),
                            alt.Tooltip("Nilai Rupiah:N", title="Nilai")
                        ]
                    )
                    .properties(height=330)
                )
                chart_header("Pagu vs Realisasi (Posisi s.d. Bulan Berjalan)")
                st.altair_chart(
                    grouped_bar.configure_axis(labelColor="#375073", titleColor="#375073", gridColor="#dbe9f8")
                        .configure_legend(labelColor="#375073")
                        .configure_view(strokeWidth=0),
                    use_container_width=True
                )

            g3, g4 = st.columns(2)

            with g3:
                serapan_chart = (
                    alt.Chart(month_summary)
                    .mark_bar(cornerRadiusEnd=7)
                    .encode(
                        y=alt.Y("Tanggal:N", sort=BULAN_LIST, title=None, axis=alt.Axis(labelOverlap=False)),
                        x=alt.X("Serapan:Q", title="Persentase Serapan", scale=alt.Scale(domain=[0, max(100, float(month_summary["Serapan"].max()) + 5)])),
                        color=alt.Color(
                            "Serapan:Q",
                            scale=alt.Scale(domain=[0, 100], range=["#315B83", "#E8C96A"]),
                            legend=None
                        ),
                        tooltip=[
                            alt.Tooltip("Tanggal:N", title="Bulan"),
                            alt.Tooltip("Serapan:Q", title="Serapan", format=".2f")
                        ]
                    )
                    .properties(height=420)
                )
                target_line = alt.Chart(pd.DataFrame({"target": [100]})).mark_rule(
                    color="#F87171", strokeDash=[6, 5], strokeWidth=2
                ).encode(x="target:Q")
                chart_header("Persentase Serapan per Bulan")
                st.altair_chart(
                    (serapan_chart + target_line)
                    .configure_axis(labelColor="#375073", titleColor="#375073", gridColor="#dbe9f8")
                    .configure_view(strokeWidth=0),
                    use_container_width=True
                )

            with g4:
                composition = pd.DataFrame({
                    "Kategori": ["Realisasi", "Sisa Anggaran"],
                    "Nilai": [total_realisasi, max(total_sisa, 0)]
                })
                composition["Nilai Rupiah"] = composition["Nilai"].apply(format_rupiah)
                donut = (
                    alt.Chart(composition)
                    .mark_arc(innerRadius=72, outerRadius=115, cornerRadius=8)
                    .encode(
                        theta=alt.Theta("Nilai:Q"),
                        color=alt.Color(
                            "Kategori:N",
                            scale=alt.Scale(domain=["Realisasi", "Sisa Anggaran"], range=["#E8C96A", "#315B83"]),
                            legend=alt.Legend(title=None, orient="bottom")
                        ),
                        tooltip=[
                            alt.Tooltip("Kategori:N"),
                            alt.Tooltip("Nilai Rupiah:N", title="Nilai")
                        ]
                    )
                    .properties(height=420)
                )
                center_text = (
                    alt.Chart(pd.DataFrame({"label": [f"{serapan:.1f}%"]}))
                    .mark_text(fontSize=28, fontWeight="bold", color="#0f172a")
                    .encode(text="label:N")
                )
                chart_header("Komposisi Anggaran")
                st.altair_chart(
                    (donut + center_text)
                    .configure_legend(labelColor="#375073")
                    .configure_view(strokeWidth=0),
                    use_container_width=True
                )

            st.subheader("Visualisasi per Unit")

            # Pagu maupun Realisasi per unit dijumlah dari snapshot TERBARU
            # tiap kegiatan (Unit+MAK) yang sudah di-dedupe lewat
            # get_latest_snapshot (variabel latest_snapshot sudah dihitung
            # di atas), supaya tidak dobel saat data mencakup banyak bulan.
            unit_summary = (
                latest_snapshot.groupby("Unit", as_index=False)[["Pagu", "Realisasi"]]
                .sum()
            )
            unit_summary["Sisa Anggaran"] = unit_summary["Pagu"] - unit_summary["Realisasi"]
            unit_summary["Serapan"] = unit_summary.apply(
                lambda row: (row["Realisasi"] / row["Pagu"] * 100) if row["Pagu"] > 0 else 0,
                axis=1
            )
            unit_summary["Pagu Rupiah"] = unit_summary["Pagu"].apply(format_rupiah)
            unit_summary["Realisasi Rupiah"] = unit_summary["Realisasi"].apply(format_rupiah)
            unit_summary["Sisa Rupiah"] = unit_summary["Sisa Anggaran"].apply(format_rupiah)

            if unit_summary.empty:
                st.info("Belum ada data unit untuk divisualisasikan")
            else:
                u1, u2 = st.columns(2)

                with u1:
                    unit_realization = (
                        alt.Chart(unit_summary)
                        .mark_bar(cornerRadiusEnd=8)
                        .encode(
                            y=alt.Y("Unit:N", sort="-x", title=None),
                            x=alt.X("Realisasi:Q", title="Realisasi", axis=rupiah_axis("Realisasi")),
                            color=alt.Color(
                                "Unit:N",
                                scale=alt.Scale(domain=UNIT_LIST, range=UNIT_COLOR_RANGE),
                                legend=None
                            ),
                            tooltip=[
                                alt.Tooltip("Unit:N", title="Unit"),
                                alt.Tooltip("Realisasi Rupiah:N", title="Realisasi")
                            ]
                        )
                        .properties(height=340)
                    )
                    chart_header("Realisasi Anggaran per Unit")
                    st.altair_chart(
                        unit_realization
                        .configure_axis(labelColor="#375073", titleColor="#375073", gridColor="#dbe9f8")
                        .configure_view(strokeWidth=0),
                        use_container_width=True
                    )

                with u2:
                    unit_long = unit_summary.melt(
                        id_vars=["Unit"],
                        value_vars=["Pagu", "Realisasi"],
                        var_name="Jenis",
                        value_name="Nilai"
                    )
                    unit_long["Nilai Rupiah"] = unit_long["Nilai"].apply(format_rupiah)
                    unit_compare = (
                        alt.Chart(unit_long)
                        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
                        .encode(
                            x=alt.X("Unit:N", title=None),
                            xOffset="Jenis:N",
                            y=alt.Y("Nilai:Q", title="Nilai Anggaran", axis=rupiah_axis("Nilai Anggaran")),
                            color=alt.Color(
                                "Jenis:N",
                                scale=alt.Scale(domain=["Pagu", "Realisasi"], range=["#4F86C6", "#E8C96A"]),
                                legend=alt.Legend(title=None, orient="top")
                            ),
                            tooltip=[
                                alt.Tooltip("Unit:N", title="Unit"),
                                alt.Tooltip("Jenis:N", title="Kategori"),
                                alt.Tooltip("Nilai Rupiah:N", title="Nilai")
                            ]
                        )
                        .properties(height=340)
                    )
                    chart_header("Pagu vs Realisasi per Unit")
                    st.altair_chart(
                        unit_compare
                        .configure_axis(labelColor="#375073", titleColor="#375073", gridColor="#dbe9f8")
                        .configure_legend(labelColor="#375073")
                        .configure_view(strokeWidth=0),
                        use_container_width=True
                    )

                u3, u4 = st.columns(2)

                with u3:
                    unit_absorption = (
                        alt.Chart(unit_summary)
                        .mark_bar(cornerRadiusEnd=8)
                        .encode(
                            y=alt.Y("Unit:N", sort="-x", title=None),
                            x=alt.X(
                                "Serapan:Q",
                                title="Persentase Serapan",
                                scale=alt.Scale(domain=[0, max(100, float(unit_summary["Serapan"].max()) + 5)])
                            ),
                            color=alt.Color(
                                "Unit:N",
                                scale=alt.Scale(domain=UNIT_LIST, range=UNIT_COLOR_RANGE),
                                legend=None
                            ),
                            tooltip=[
                                alt.Tooltip("Unit:N", title="Unit"),
                                alt.Tooltip("Serapan:Q", title="Serapan", format=".2f")
                            ]
                        )
                        .properties(height=340)
                    )
                    target_unit = alt.Chart(pd.DataFrame({"target": [100]})).mark_rule(
                        color="#F87171", strokeDash=[6, 5], strokeWidth=2
                    ).encode(x="target:Q")
                    chart_header("Persentase Serapan per Unit")
                    st.altair_chart(
                        (unit_absorption + target_unit)
                        .configure_axis(labelColor="#375073", titleColor="#375073", gridColor="#dbe9f8")
                        .configure_view(strokeWidth=0),
                        use_container_width=True
                    )

                with u4:
                    unit_share = unit_summary[["Unit", "Realisasi"]].copy()
                    unit_share = unit_share[unit_share["Realisasi"] > 0]
                    unit_share["Realisasi Rupiah"] = unit_share["Realisasi"].apply(format_rupiah)
                    unit_donut = (
                        alt.Chart(unit_share)
                        .mark_arc(innerRadius=68, outerRadius=112, cornerRadius=7)
                        .encode(
                            theta=alt.Theta("Realisasi:Q"),
                            color=alt.Color(
                                "Unit:N",
                                scale=alt.Scale(domain=UNIT_LIST, range=UNIT_COLOR_RANGE),
                                legend=alt.Legend(title=None, orient="bottom")
                            ),
                            tooltip=[
                                alt.Tooltip("Unit:N", title="Unit"),
                                alt.Tooltip("Realisasi Rupiah:N", title="Realisasi")
                            ]
                        )
                        .properties(height=340)
                    )
                    chart_header("Kontribusi Realisasi per Unit")
                    st.altair_chart(
                        unit_donut
                        .configure_legend(labelColor="#375073", columns=2)
                        .configure_view(strokeWidth=0),
                        use_container_width=True
                    )

                st.subheader("Ringkasan per Unit")
                unit_display = unit_summary[["Unit", "Pagu", "Realisasi", "Sisa Anggaran", "Serapan"]].copy()
                unit_display["Pagu"] = unit_display["Pagu"].apply(format_rupiah)
                unit_display["Realisasi"] = unit_display["Realisasi"].apply(format_rupiah)
                unit_display["Sisa Anggaran"] = unit_display["Sisa Anggaran"].apply(format_rupiah)
                unit_display["Serapan"] = unit_display["Serapan"].apply(lambda x: f"{x:.2f}%".replace(".", ","))
                render_summary_table(unit_display)

            st.subheader("Ringkasan Bulanan")
            monthly_display = month_summary[["Tanggal", "Pagu", "Realisasi", "Sisa Anggaran", "Serapan"]].copy()
            monthly_display["Pagu"] = monthly_display["Pagu"].apply(format_rupiah)
            monthly_display["Realisasi"] = monthly_display["Realisasi"].apply(format_rupiah)
            monthly_display["Sisa Anggaran"] = monthly_display["Sisa Anggaran"].apply(format_rupiah)
            monthly_display["Serapan"] = monthly_display["Serapan"].apply(lambda x: f"{x:.2f}%".replace(".", ","))
            render_summary_table(monthly_display)

        st.subheader("Detail Data")
        display_df = display_data(filtered)
        render_summary_table(display_df)

        format_download = st.selectbox(
            "Format Download Data",
            ["Excel (.xlsx)", "CSV (.csv)"],
            key="format_download_data"
        )

        if format_download == "Excel (.xlsx)":
            xlsx_export = to_xlsx(display_df)
            if xlsx_export is not None:
                st.download_button(
                    "Download Data",
                    data=xlsx_export,
                    file_name="Monitoring_Anggaran.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.download_button(
                "Download Data",
                data=to_csv(display_df),
                file_name="Monitoring_Anggaran.csv",
                mime="text/csv"
            )

        if not is_admin():
            st.info("Akun Operator hanya dapat input, upload, lihat, dan download data")


# =========================================================
# KELOLA DATA - KHUSUS ADMIN
# =========================================================
elif menu == "Kelola Data":
    if not is_admin():
        st.error("Akses ditolak")
        st.stop()

    st.subheader("Kelola Data")

    with st.container(key="refresh_btn_kelola_data"):
        if st.button("🔄 Refresh Data"):
            st.rerun()

    df_raw = fetch_data()

    if df_raw.empty:
        st.warning("Belum ada data yang bisa dikelola")
    else:
        st.caption("Admin bisa mengubah data langsung di tabel, lalu klik Simpan Perubahan.")

        kelola_unit = st.selectbox(
            "Filter Unit (opsional)",
            ["Semua Unit"] + UNIT_LIST,
            key="kelola_filter_unit",
            help="Pilih salah satu unit supaya cuma data unit itu yang muncul di tabel edit."
        )

        if kelola_unit == "Semua Unit":
            editable_df = df_raw.copy()
        else:
            editable_df = df_raw[df_raw["Unit"] == kelola_unit].copy()

        if editable_df.empty:
            st.info(f"Belum ada data untuk unit {kelola_unit}.")
        else:
            # Kolom "id" disembunyikan dari tampilan tapi tetap dipakai
            # untuk mencocokkan baris mana yang diubah di Supabase.
            editable_df = editable_df.reset_index(drop=True)
            editable_df["No"] = range(1, len(editable_df) + 1)

            # Celah biar tetap ada titik ribuan pas ngedit: Pagu/Realisasi
            # ditampilkan sebagai kolom TEKS berformat ("100.000.000"),
            # bukan kolom angka murni (yang menurut keterbatasan Streamlit
            # tidak bisa diformat titik ribuan). Saat disimpan, titiknya
            # dibuang lagi lewat clean_money() supaya kembali jadi angka.
            display_edit_df = editable_df.copy()
            display_edit_df["Pagu"] = display_edit_df["Pagu"].apply(
                lambda v: f"{float(v):,.0f}".replace(",", ".")
            )
            display_edit_df["Realisasi"] = display_edit_df["Realisasi"].apply(
                lambda v: f"{float(v):,.0f}".replace(",", ".")
            )
            display_edit_df["Sisa Anggaran"] = display_edit_df["Sisa Anggaran"].apply(
                lambda v: f"{float(v):,.0f}".replace(",", ".")
            )

            edited_df = st.data_editor(
                display_edit_df,
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
                disabled=["id", "No", "Sisa Anggaran"],
                column_config={
                    "id": None,  # sembunyikan kolom id dari tampilan
                    "Tanggal": st.column_config.SelectboxColumn(
                        "Tanggal", options=BULAN_LIST, required=True
                    ),
                    "No": st.column_config.NumberColumn("No"),
                    "MAK": st.column_config.TextColumn("MAK", required=True),
                    "Kegiatan": st.column_config.TextColumn("Kegiatan", required=True),
                    "Pagu": st.column_config.TextColumn("Pagu (Rp)"),
                    "Realisasi": st.column_config.TextColumn("Realisasi (Rp)"),
                    "Sisa Anggaran": st.column_config.TextColumn("Sisa Anggaran (Rp)"),
                },
                key="admin_editor"
            )

            if st.button("Simpan Perubahan", use_container_width=True):
                # Parse ulang kolom Pagu/Realisasi dari teks berformat titik
                # ("100.000.000") balik jadi angka sebelum dibandingkan/disimpan.
                edited_df_parsed = edited_df.copy()
                edited_df_parsed["Pagu"] = edited_df_parsed["Pagu"].apply(clean_money)
                edited_df_parsed["Realisasi"] = edited_df_parsed["Realisasi"].apply(clean_money)
                edited_df_norm = normalize_data(edited_df_parsed, keep_id=True)
                original_norm = normalize_data(editable_df, keep_id=True)

                # Cuma kirim baris yang BENERAN berubah -- dibandingkan
                # dengan data sebelum diedit, biar nggak nulis ulang baris
                # yang isinya sama persis kayak sebelumnya.
                compare_cols = ["Unit", "Tanggal", "MAK", "Kegiatan", "Pagu", "Realisasi"]
                merged = edited_df_norm.merge(
                    original_norm, on="id", suffixes=("_new", "_old")
                )
                changed_mask = (
                    merged[[f"{c}_new" for c in compare_cols]].values
                    != merged[[f"{c}_old" for c in compare_cols]].values
                ).any(axis=1)
                changed_ids = merged.loc[changed_mask, "id"].tolist()
                rows_to_save = edited_df_norm[edited_df_norm["id"].isin(changed_ids)]

                if rows_to_save.empty:
                    st.info("Tidak ada perubahan yang perlu disimpan.")
                else:
                    try:
                        with st.spinner(f"Menyimpan {len(rows_to_save)} baris yang berubah ke Supabase..."):
                            update_rows_bulk(rows_to_save)
                        st.success(f"{len(rows_to_save)} baris perubahan berhasil disimpan ke Supabase")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Gagal menyimpan perubahan: {exc}")

        st.divider()
        st.subheader("Hapus Data")

        hapus_unit = st.selectbox(
            "Filter Unit",
            UNIT_LIST,
            index=UNIT_LIST.index(df_raw["Unit"].mode()[0]) if not df_raw.empty and df_raw["Unit"].mode().size else 0,
            key="hapus_filter_unit"
        )
        df_hapus = df_raw[df_raw["Unit"] == hapus_unit].sort_values("id", ascending=False)

        if df_hapus.empty:
            st.info(f"Belum ada data untuk unit {hapus_unit}.")
            selected_rows = []
        else:
            id_terbaru = df_raw["id"].max()
            delete_options = df_hapus["id"].tolist()
            selected_rows = st.multiselect(
                f"Pilih kegiatan yang mau dihapus (Unit: {hapus_unit})",
                options=delete_options,
                format_func=lambda row_id: (
                    f"{'🆕 ' if row_id == id_terbaru else ''}"
                    f"{df_raw.loc[df_raw['id'] == row_id, 'Tanggal'].values[0]} | "
                    f"{df_raw.loc[df_raw['id'] == row_id, 'MAK'].values[0]} | "
                    f"{df_raw.loc[df_raw['id'] == row_id, 'Kegiatan'].values[0]}"
                    f"{' (data paling baru ditambahkan)' if row_id == id_terbaru else ''}"
                )
            )

        confirm_delete = st.checkbox("Saya yakin mau menghapus data yang dipilih")

        if st.button(
            "Hapus Data Terpilih",
            use_container_width=True,
            type="primary",
            disabled=not selected_rows or not confirm_delete
        ):
            try:
                delete_rows(selected_rows)
                st.success(f"{len(selected_rows)} data berhasil dihapus dari Supabase")
                st.rerun()
            except Exception as exc:
                st.error(f"Gagal menghapus data: {exc}")
