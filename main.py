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
    width: 72px; height: 72px; margin: 0 auto 18px auto;
    border-radius: 22px; display: flex; align-items: center;
    justify-content: center; font-size: 34px;
    background: linear-gradient(135deg, #C8A951, #ead58f);
    box-shadow: 0 10px 24px rgba(200,169,81,.35);
}
.login-title { text-align: center; font-size: 30px; font-weight: 800; color: #0f172a !important; }
.login-subtitle { text-align: center; color: #64748b !important; margin-bottom: 28px; }
.user-card {
    background: #f8fafc;
    border: 1px solid #cfe3f7;
    border-radius: 16px; padding: 14px; margin: 10px 0 18px 0;
}
.user-name { font-weight: 800; color: #0f172a !important; }
.user-role { font-size: 12px; color: #64748b !important; }
</style>
""", unsafe_allow_html=True)

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


def delete_rows(ids):
    ids = [int(i) for i in ids]
    if ids:
        supabase.table(TABLE_NAME).delete().in_("id", ids).execute()


def show_login():
    st.markdown("""
    <div class="login-wrap">
        <div class="login-logo"><img src="data:image/png;base64,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" style="height:44px;" /></div>
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

logo_col1, logo_col2 = st.sidebar.columns([1, 1])
with logo_col1:
    st.image("unj_final.png", width=60)
with logo_col2:
    st.image("kemenperin_final.png", width=90)

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
    <div class="gov-header-title" style="color:#ffffff !important;display:flex;align-items:center;gap:12px;"><img src="data:image/png;base64,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" style="height:36px;" />Sistem Informasi Realisasi Anggaran (SIRA)</div>
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

    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            unit = st.selectbox("Unit", UNIT_LIST)
            tanggal = st.selectbox("Tanggal (Bulan)", BULAN_LIST)
            mak = st.text_input("MAK", placeholder="Contoh: 521211")
            kegiatan = st.text_area("Kegiatan")
        with col2:
            pagu = st.number_input("Pagu (Rp)", min_value=0, step=1_000_000)
            realisasi = st.number_input("Realisasi (Rp)", min_value=0, step=1_000_000)
            sisa = pagu - realisasi
            st.info(f"Sisa Anggaran: {format_rupiah(sisa)}")

        submitted = st.form_submit_button("Simpan Data", use_container_width=True)

    if submitted:
        if not mak.strip() or not kegiatan.strip():
            st.error("MAK dan Kegiatan wajib diisi")
        else:
            try:
                insert_row(unit, tanggal, mak.strip(), kegiatan.strip(), pagu, realisasi)
                st.success("Data berhasil disimpan ke Supabase")
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

            edited_df = st.data_editor(
                editable_df,
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
                    "Pagu": st.column_config.NumberColumn("Pagu", min_value=0, format="Rp %.0f"),
                    "Realisasi": st.column_config.NumberColumn("Realisasi", min_value=0, format="Rp %.0f"),
                    "Sisa Anggaran": st.column_config.NumberColumn("Sisa Anggaran", format="Rp %.0f"),
                },
                key="admin_editor"
            )

            if st.button("Simpan Perubahan", use_container_width=True):
                edited_df = normalize_data(edited_df, keep_id=True)
                errors = []
                with st.spinner("Menyimpan perubahan ke Supabase..."):
                    for _, row in edited_df.iterrows():
                        try:
                            update_row(
                                row["id"], row["Unit"], row["Tanggal"], row["MAK"],
                                row["Kegiatan"], row["Pagu"], row["Realisasi"]
                            )
                        except Exception as exc:
                            errors.append(f"ID {row['id']}: {exc}")

                if errors:
                    st.error("Sebagian data gagal disimpan:\n" + "\n".join(errors))
                else:
                    st.success("Perubahan berhasil disimpan ke Supabase")
                    st.rerun()

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
