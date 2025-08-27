import streamlit as st
import pandas as pd
from datetime import datetime

# ===== 💡 CSS Kalbe =====
st.markdown("""
    <style>
        .stApp { background-color: #e8f5e9; color: #1b5e20; }
        label, .stTextInput label, .stTextInput > div > label,
        .stMarkdown, .stInfo, .stWarning { color: #1b5e20 !important; font-weight: bold; }
        .stTextInput > div > div > input {
            background-color: #ffffff !important; color: #1b5e20 !important;
            border: 1px solid #81c784; font-weight: bold;
        }
        .stAlert-success { background-color: #c8e6c9 !important; color: #1b5e20 !important;
            font-weight: bold; font-size: 16px; border-radius: 8px; padding: 0.5em 1em; }
        .stAlert-warning { background-color: #fff3cd !important; color: #795548 !important; }
        .stAlert-info { background-color: #d0f0fd !important; color: #0277bd !important; }
        h1, h2, h3, h4, h5 { color: #1b5e20; font-weight: 800; text-align: center; }
        .stDataFrame { background-color: #ffffff; color: #000000; }
        div.stButton > button, button[aria-label="🔍 Cari Data"] {
            background-color: #1b5e20 !important; color: white !important; border: none;
            border-radius: 6px; font-weight: bold; padding: 0.5em 1.5em; transition: 0.3s ease;
        }
        div.stButton > button[kind="primary"]:hover,
        div.stButton > button[aria-label="🔍 Cari Data"]:hover {
            background-color: #2e7d32 !important; color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# ===== 🖼️ Logo Kalbe =====
st.image("kalbe.png", width=200)

# ===== 🧾 Judul =====
st.title("🔍 Pencarian Data Kendaraan")
st.markdown("<h4 style='text-align: center;'>PT Kalbe Morinaga Indonesia</h4>", unsafe_allow_html=True)

# ===== 📦 Load Data (semua kolom sebagai string agar leading zero aman) =====
data = pd.read_csv('data_kendaraan.csv', dtype=str)
# rapikan nama kolom & isi sel (hapus spasi depan/belakang)
data.columns = data.columns.str.strip()
data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

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

# ===== 🔍 Form Pencarian =====
with st.form("form_pencarian"):
    query = st.text_input("Masukkan NIK atau No.Plat (Mobil/Motor):")
    submit = st.form_submit_button("🔍 Cari Data")

# ===== 🧩 Kolom pencarian: NIK + semua No.Plat* =====
plate_cols = [c for c in data.columns if c.lower().startswith("no.plat")]
searchable_cols = [c for c in ["NIK"] + plate_cols if c in data.columns]

# ===== 🔎 Proses Pencarian =====
if submit:
    q = query.strip()
    if q == "":
        st.info("Silakan masukkan kata kunci untuk mencari data kendaraan.")
    else:
        # bangun mask pencarian (literal match, bukan regex)
        mask = pd.Series(False, index=data.index)
        for col in searchable_cols:
            mask |= data[col].str.contains(q, case=False, na=False, regex=False)

        results = data[mask]

        if not results.empty:
            st.success(f"Ditemukan {len(results)} hasil untuk '{q}'")
            st.dataframe(results.style.apply(highlight_expired, axis=1), use_container_width=True)
        else:
            st.warning(f"Tidak ditemukan hasil untuk '{q}'")
else:
    st.info("Silakan masukkan kata kunci untuk mencari data kendaraan.")
