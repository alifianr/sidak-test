import streamlit as st
import pandas as pd
import re

# ===== 🔧 Page setup =====
st.set_page_config(page_title="Pencarian Data Kendaraan", page_icon="🔍", layout="centered")

# ===== 💡 CSS Custom untuk Kalbe Style =====
st.markdown("""
    <style>
        .stApp { background-color: #e8f5e9; color: #1b5e20; }

        label, .stTextInput label, .stTextInput > div > label,
        .stMarkdown, .stInfo, .stWarning {
            color: #1b5e20 !important;
            font-weight: bold;
        }

        .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #1b5e20 !important;
            border: 1px solid #81c784;
            font-weight: bold;
        }

        /* ✅ Alert Box: Success */
        .stAlert-success {
            background-color: #111 !important;
            color: #fff !important;
            font-weight: 600;
            font-size: 16px;
            border-radius: 10px;
            padding: 14px 16px;
        }

        .stAlert-warning { background-color: #fff3cd !important; color: #795548 !important; }
        .stAlert-info { background-color: #d0f0fd !important; color: #0277bd !important; }

        h1, h2, h3, h4, h5 {
            color: #1b5e20; font-weight: 800; text-align: center;
        }

        .stDataFrame { background-color: #ffffff; color: #000000; }

        /* ✅ Tombol submit styling */
        div.stButton > button,
        button[aria-label="🔍 Cari Data"] {
            background-color: #0f172a !important;   /* gelap seperti contoh */
            color: white !important;
            border: none; border-radius: 10px;
            font-weight: 700; padding: 0.6rem 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,.15);
            transition: 0.3s ease;
        }
        div.stButton > button[kind="primary"]:hover,
        div.stButton > button[aria-label="🔍 Cari Data"]:hover {
            background-color: #111827 !important; color: white !important;
        }

        /* Banner info hitam di bawah input */
        .info-banner{
            background:#111; color:#fff; border-radius:10px;
            padding:14px 16px; font-weight:600; margin: 8px 0 20px 0;
        }
        .error-banner{
            background:#dc2626;     
            color:#fff;
            border-radius:10px;
            padding:14px 16px;
            font-weight:600;
            margin:8px 0 20px 0;     
        }   
        
    </style>
""", unsafe_allow_html=True)

# ===== 🖼️ Logo Kalbe =====
st.image("kalbe.png", width=200)

# ===== 🧾 Judul Utama =====
st.title("🔍 Pencarian Data Kendaraan")
st.markdown("<h4 style='text-align: center;'>PT Kalbe Morinaga Indonesia</h4>", unsafe_allow_html=True)

# ===== 📦 Load Data (CSV kamu pakai ; dan banyak kolom Unnamed) =====
data = pd.read_csv('data_kendaraan.csv', sep=';', dtype=str, engine='python', on_bad_lines='skip')
data.columns = data.columns.str.strip().str.replace(r"\s+", " ", regex=True)
# buang kolom Unnamed yang kosong total
to_drop = [c for c in data.columns if c.startswith("Unnamed:") and data[c].fillna("").eq("").all()]
if to_drop: data = data.drop(columns=to_drop)
# rapikan isi sel
data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# ===== 🧠 Helper normalisasi teks (supaya plat dengan spasi/dash tetap cocok) =====
def norm_text(s: str) -> str:
    if not isinstance(s, str): return ""
    return re.sub(r"[^A-Z0-9]", "", s.upper())

# ===== ✅ Kolom tanggal (struktur baru) =====
DATE_COLS = [
    "Masa Berlaku SIM Mobil",
    "Masa Berlaku STNK Mobil ke-1",
    "Masa Berlaku SIM Motor",
    "Masa Berlaku STNK Motor ke-1",
    "Masa Berlaku STNK Motor ke-2",
    "Masa Berlaku STNK Motor ke-3",
]
date_cols_present = [c for c in DATE_COLS if c in data.columns]

# ===== 🎨 Highlight baris kadaluarsa =====
def highlight_expired(row):
    now = pd.Timestamp.now().normalize()
    for col in date_cols_present:
        dt = pd.to_datetime(row.get(col, pd.NaT), errors='coerce', dayfirst=True)
        if pd.notnull(dt) and dt < now:
            return ['background-color: #ffcccc; color: red; font-weight: bold'] * len(row)
    return [''] * len(row)

# ===== 🔎 Siapkan kolom pencarian: NIK + Nama + semua No.Plat =====
searchable_cols = []
if "NIK" in data.columns: searchable_cols.append("NIK")
name_cols = [c for c in data.columns if re.search(r"\bnama\b", c, flags=re.IGNORECASE)]
if name_cols: searchable_cols.append(name_cols[0])  # ex: "Nama Lengkap (324)"
plate_cols = [c for c in data.columns if ("No.Plat" in c) or ("No. Plat" in c) or ("Plat " in c)]
searchable_cols += plate_cols

# ===== 🔍 Input & tombol (tanpa st.form agar tidak ada 'Press Enter...') =====
query = st.text_input("Masukkan Nama, NIK, atau No.Plat Kendaraan:", placeholder="Contoh: B1234ABC / 3201xxxx / RAKHA")
clicked = st.button("🔍 Cari Data")

# ===== 🔎 Proses Pencarian =====
if clicked:
    q = query.strip()
    if q == "":
        st.markdown('<div class="info-banner">Silakan masukkan kata kunci untuk mencari data kendaraan.</div>', unsafe_allow_html=True)
    elif not searchable_cols:
        st.markdown('<div class="info-banner">Kolom pencarian tidak ditemukan. Cek NIK/Nama/No.Plat di CSV.</div>', unsafe_allow_html=True)
    else:
        qn = norm_text(q)
        mask = pd.Series(False, index=data.index)
        for col in searchable_cols:
            mask |= data[col].fillna("").map(norm_text).str.contains(qn, regex=False)

        results = data[mask]
        if not results.empty:
            st.markdown(f"<div class='info-banner'>Ditemukan {len(results)} hasil untuk '{q}'</div>", unsafe_allow_html=True)
            st.dataframe(results.style.apply(highlight_expired, axis=1), use_container_width=True)
        else:
            st.markdown(f'<div class="error-banner">Tidak ditemukan hasil untuk "{q}".</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="info-banner">Silakan masukkan kata kunci untuk mencari data kendaraan.</div>', unsafe_allow_html=True)
