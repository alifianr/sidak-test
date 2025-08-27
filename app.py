import streamlit as st
import pandas as pd
import re

# ===== CSS singkat =====
st.markdown("""
<style>
.stApp { background-color:#e8f5e9; color:#1b5e20; }
h1,h2,h3,h4,h5 { color:#1b5e20; font-weight:800; text-align:center; }
div.stButton>button, button[aria-label="🔍 Cari Data"] {
  background-color:#1b5e20 !important; color:#fff !important; border:none; border-radius:6px;
  font-weight:bold; padding:.5em 1.5em;
}
</style>
""", unsafe_allow_html=True)

# ===== Header =====
st.image("kalbe.png", width=200)
st.title("🔍 Pencarian Data Kendaraan")
st.markdown("<h4 style='text-align: center;'>PT Kalbe Morinaga Indonesia</h4>", unsafe_allow_html=True)

# ===== Load Data: pakai separator ';' dan semua kolom string =====
# on_bad_lines='skip' untuk menghindari baris tidak rapi
data = pd.read_csv("data_kendaraan.csv", sep=";", dtype=str, engine="python", on_bad_lines="skip")

# Rapikan nama kolom: strip + ganti spasi ganda jadi satu
data.columns = data.columns.str.strip().str.replace(r"\s+", " ", regex=True)

# Buang kolom Unnamed yang biasanya kosong
to_drop = [c for c in data.columns if c.startswith("Unnamed:")]
# drop hanya jika seluruh kolomnya NA/empty
empty_unnamed = [c for c in to_drop if data[c].dropna().eq("").all()]
data = data.drop(columns=empty_unnamed)

# Rapikan isi sel (strip)
data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# ===== Helper normalisasi untuk pencarian (hapus non-alfanumerik, uppercase) =====
def norm_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    return re.sub(r"[^A-Z0-9]", "", s.upper())

# ===== Kolom tanggal sesuai struktur baru =====
DATE_COLS = [
    "Masa Berlaku SIM Mobil",
    "Masa Berlaku STNK Mobil ke-1",
    "Masa Berlaku SIM Motor",
    "Masa Berlaku STNK Motor ke-1",
    "Masa Berlaku STNK Motor ke-2",
    "Masa Berlaku STNK Motor ke-3",
]
date_cols_present = [c for c in DATE_COLS if c in data.columns]

# ===== Highlight baris kadaluarsa =====
def highlight_expired(row):
    now = pd.Timestamp.now().normalize()
    for col in date_cols_present:
        dt = pd.to_datetime(row.get(col, pd.NaT), errors="coerce", dayfirst=True)
        if pd.notnull(dt) and dt < now:
            return ["background-color:#ffcccc; color:red; font-weight:bold"] * len(row)
    return [""] * len(row)

# ===== Deteksi kolom pencarian =====
# 1) NIK (kalau ada)
searchable_cols = [c for c in ["NIK"] if c in data.columns]

# 2) Nama: cari kolom yang mengandung kata "Nama" (mis. "Nama Lengkap (324)")
name_cols = [c for c in data.columns if re.search(r"\bnama\b", c, flags=re.IGNORECASE)]
# ambil satu kolom nama yang paling relevan (atau semua kalau mau)
if name_cols:
    searchable_cols.append(name_cols[0])

# 3) Semua kolom No.Plat (variasi: Mobil/Motor, spasi ganda, dll)
plate_cols = [c for c in data.columns if "No.Plat" in c or "No. Plat" in c or "Plat " in c]
searchable_cols += plate_cols

# ===== Form =====
with st.form("form_pencarian"):
    query = st.text_input("Masukkan Nama, NIK, atau No.Plat (Mobil/Motor):")
    submit = st.form_submit_button("🔍 Cari Data")

# ===== Pencarian =====
if submit:
    q = query.strip()
    if q == "":
        st.info("Silakan masukkan kata kunci untuk mencari data kendaraan.")
    else:
        qn = norm_text(q)
        if not searchable_cols:
            st.warning("Kolom untuk pencarian tidak ditemukan. Cek NIK/Nama/No.Plat di CSV.")
        else:
            mask = pd.Series(False, index=data.index)
            for col in searchable_cols:
                col_norm = data[col].fillna("").map(norm_text)
                mask |= col_norm.str.contains(qn, case=False, na=False, regex=False)

            results = data[mask]

            if not results.empty:
                st.success(f"Ditemukan {len(results)} hasil untuk '{q}'")
                st.dataframe(results.style.apply(highlight_expired, axis=1), use_container_width=True)
            else:
                st.warning(f"Tidak ditemukan hasil untuk '{q}'")
else:
    st.info("Silakan masukkan kata kunci untuk mencari data kendaraan.")
