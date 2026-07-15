import streamlit as st
import pandas as pd
import altair as alt
from io import BytesIO
import time
from supabase import create_client, Client

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

/* Tombol aksi utama (Simpan, Masuk, Upload, dsb) = MERAH, disamakan
   dengan warna tombol Logout */
.stButton button,
.stFormSubmitButton button {
    background: linear-gradient(135deg, #dc2626, #ef4444) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 18px rgba(220,38,38,.22);
}
/* Tombol download = KUNING/EMAS (aksen brand) */
.stDownloadButton button {
    background: linear-gradient(135deg, #C8A951, #d8bc6b) !important;
    color: #1e293b !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
}
/* Tombol destruktif (type="primary", dipakai untuk Hapus Data) = MERAH */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #dc2626, #ef4444) !important;
    color: #ffffff !important;
    box-shadow: 0 8px 18px rgba(220,38,38,.25);
}
/* Tombol Logout di sidebar = MERAH */
[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, #dc2626, #ef4444) !important;
    color: #ffffff !important;
}
/* Tombol Refresh Data = BIRU (bukan hijau, biar beda dari aksi simpan) */
.st-key-refresh_btn_lihat_semua .stButton button,
.st-key-refresh_btn_kelola_data .stButton button {
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    color: #ffffff !important;
    box-shadow: 0 8px 18px rgba(37,99,235,.25);
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
[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1.5px solid #bcd9f4;
}
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
    bukan ditambahkan sebagai baris baru sehingga tidak dobel hitung."""
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
        <div class="login-logo">🏛️</div>
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
    <div class="gov-header-title" style="color:#ffffff !important;">🏛️ Sistem Informasi Realisasi Anggaran (SIRA)</div>
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
                st.dataframe(display_data(upload_df), use_container_width=True, hide_index=True)

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
                        insert_bulk(upload_df)
                        st.toast("Upload sukses, data udah masuk 😹", icon="✅")
                        st.success(
                            f"Upload berhasil. {len(upload_df)} baris data udah disimpan ke Supabase."
                        )
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
                    .properties(height=330, title="Tren Realisasi per Bulan")
                )
                st.altair_chart(
                    area.configure_title(color="#0f2d52", fontSize=17, anchor="start")
                        .configure_axis(labelColor="#375073", titleColor="#375073", gridColor="#dbe9f8")
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
                    .properties(height=330, title="Pagu vs Realisasi (Posisi s.d. Bulan Berjalan)")
                )
                st.altair_chart(
                    grouped_bar.configure_title(color="#0f2d52", fontSize=17, anchor="start")
                        .configure_axis(labelColor="#375073", titleColor="#375073", gridColor="#dbe9f8")
                        .configure_legend(labelColor="#375073")
                        .configure_view(strokeWidth=0),
                    use_container_width=True
                )

            g3, g4 = st.columns([1.35, 1])

            with g3:
                serapan_chart = (
                    alt.Chart(month_summary)
                    .mark_bar(cornerRadiusEnd=7)
                    .encode(
                        y=alt.Y("Tanggal:N", sort=BULAN_LIST, title=None),
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
                    .properties(height=330, title="Persentase Serapan per Bulan")
                )
                target_line = alt.Chart(pd.DataFrame({"target": [100]})).mark_rule(
                    color="#F87171", strokeDash=[6, 5], strokeWidth=2
                ).encode(x="target:Q")
                st.altair_chart(
                    (serapan_chart + target_line)
                    .configure_title(color="#0f2d52", fontSize=17, anchor="start")
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
                    .properties(height=330, title="Komposisi Anggaran")
                )
                center_text = (
                    alt.Chart(pd.DataFrame({"label": [f"{serapan:.1f}%"]}))
                    .mark_text(fontSize=28, fontWeight="bold", color="#0f172a")
                    .encode(text="label:N")
                )
                st.altair_chart(
                    (donut + center_text)
                    .configure_title(color="#0f2d52", fontSize=17, anchor="start")
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
                                "Realisasi:Q",
                                scale=alt.Scale(range=["#315B83", "#E8C96A"]),
                                legend=None
                            ),
                            tooltip=[
                                alt.Tooltip("Unit:N", title="Unit"),
                                alt.Tooltip("Realisasi Rupiah:N", title="Realisasi")
                            ]
                        )
                        .properties(height=340, title="Realisasi Anggaran per Unit")
                    )
                    st.altair_chart(
                        unit_realization.configure_title(color="#0f2d52", fontSize=17, anchor="start")
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
                        .properties(height=340, title="Pagu vs Realisasi per Unit")
                    )
                    st.altair_chart(
                        unit_compare.configure_title(color="#0f2d52", fontSize=17, anchor="start")
                        .configure_axis(labelColor="#375073", titleColor="#375073", gridColor="#dbe9f8")
                        .configure_legend(labelColor="#375073")
                        .configure_view(strokeWidth=0),
                        use_container_width=True
                    )

                u3, u4 = st.columns([1.3, 1])

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
                                "Serapan:Q",
                                scale=alt.Scale(domain=[0, 100], range=["#315B83", "#E8C96A"]),
                                legend=None
                            ),
                            tooltip=[
                                alt.Tooltip("Unit:N", title="Unit"),
                                alt.Tooltip("Serapan:Q", title="Serapan", format=".2f")
                            ]
                        )
                        .properties(height=340, title="Persentase Serapan per Unit")
                    )
                    target_unit = alt.Chart(pd.DataFrame({"target": [100]})).mark_rule(
                        color="#F87171", strokeDash=[6, 5], strokeWidth=2
                    ).encode(x="target:Q")
                    st.altair_chart(
                        (unit_absorption + target_unit)
                        .configure_title(color="#0f2d52", fontSize=17, anchor="start")
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
                            color=alt.Color("Unit:N", legend=alt.Legend(title=None, orient="bottom")),
                            tooltip=[
                                alt.Tooltip("Unit:N", title="Unit"),
                                alt.Tooltip("Realisasi Rupiah:N", title="Realisasi")
                            ]
                        )
                        .properties(height=340, title="Kontribusi Realisasi per Unit")
                    )
                    st.altair_chart(
                        unit_donut.configure_title(color="#0f2d52", fontSize=17, anchor="start")
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
                st.dataframe(unit_display, use_container_width=True, hide_index=True)

            st.subheader("Ringkasan Bulanan")
            monthly_display = month_summary[["Tanggal", "Pagu", "Realisasi", "Sisa Anggaran", "Serapan"]].copy()
            monthly_display["Pagu"] = monthly_display["Pagu"].apply(format_rupiah)
            monthly_display["Realisasi"] = monthly_display["Realisasi"].apply(format_rupiah)
            monthly_display["Sisa Anggaran"] = monthly_display["Sisa Anggaran"].apply(format_rupiah)
            monthly_display["Serapan"] = monthly_display["Serapan"].apply(lambda x: f"{x:.2f}%".replace(".", ","))
            st.dataframe(monthly_display, use_container_width=True, hide_index=True)

        st.subheader("Detail Data")
        display_df = display_data(filtered)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

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

        # Kolom "id" disembunyikan dari tampilan tapi tetap dipakai
        # untuk mencocokkan baris mana yang diubah di Supabase.
        editable_df = df_raw.copy()

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

        delete_options = df_raw["id"].tolist()
        selected_rows = st.multiselect(
            "Pilih data yang mau dihapus",
            options=delete_options,
            format_func=lambda row_id: (
                f"No {df_raw.loc[df_raw['id'] == row_id, 'No'].values[0]} | "
                f"{df_raw.loc[df_raw['id'] == row_id, 'MAK'].values[0]} | "
                f"{df_raw.loc[df_raw['id'] == row_id, 'Kegiatan'].values[0]}"
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
