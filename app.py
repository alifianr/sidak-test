import streamlit as st
import pandas as pd
import re

# ===== Page setup =====
st.set_page_config(page_title="Pencarian Data Kendaraan", page_icon="🔍", layout="centered")

# ===== CSS (gaya tampilan kedua) =====
st.markdown("""
<style>
:root{
  --kalbe-green:#1b5e20; --bg:#e8f5e9; --soft:#f1f8e9; --border:#c8e6c9; --dark:#0f172a;
}
.stApp{ background-color:var(--bg); color:var(--kalbe-green); }

h1,h2,h3,h4,h5{ color:var(--kalbe-green); font-weight:800; text-align:center; }

.k-card{
  background:var(--soft); border:1px solid var(--border);
  border-radius:12px; padding:18px 20px; margin:16px 0;
  box-shadow:0 4px 12px rgba(0,0,0,.06);
}

.k-input input{
  background:#fff !important; color:#1b5e20 !important; font-weight:600 !important;
  border:2px solid #2e7d32 !important; border-radius:8px !important;
  padding:10px 14px !important;
}

div.stButton>button{
  background:var(--dark) !important; color:#fff !important;
  border-radius:10px; border:none; padding:.6rem 1.2rem; font-weight:700;
  box-shadow:0 2px 8px rgba(0,0,0,.15);
}

.info-banner{
  background:#111; color:#fff; border-radius:10px; padding:14px 16px;
  font-weight:600; margin-top:8px;
}

.stAlert-success{
  background-color:#c8e6c9 !important; color:#1b5e20 !important;
  font-weight:700; border-radius:10px;
}

.stDataFrame [data-testid="stTable"] thead tr th{
  background:var(--dark) !important; color:#fff !important; font-weight:800 !important;
}
.stDataFrame div[role="columnheader"]{
  background:var(--dark) !important; color:#fff !important; font-weight:800 !important;
}
</style>
""", unsafe_allow_html=True)

# ===== Header =====
st.image("kalbe.png", width=180)  # letak kiri-atas
st.markdown("<h1>🔍 Pencarian Data Kendaraan</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;margin-top:-6px;'>PT Kalbe Morinaga Indonesia</h4>", unsafe_allow_html=True)

# ===== Load data (CSV pakai ';') =====
data = pd.read_csv("data_kendaraan.csv", sep=";", dtype=str, engine="python", on_bad_lines="skip")
data.columns = data.columns.str.strip().str.replace(r"\s+", " ", regex=True)
# buang kolom Unnamed kosong
to_drop = [c for c in data.columns if c.startswith("Unnamed:") and data[c].fillna("").eq("").all()]
data = data.drop(columns=to_drop)
data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# ===== Helpers =====
def norm_text(s: str) -> str:
    if not isinstance(s, str): return ""
    return re.sub(r"[^A-Z0-9]", "", s.upper())

DATE_COLS = [
    "Masa Berlaku SIM Mobil",
    "Masa Berlaku STNK Mobil ke-1",
    "Masa Berlaku SIM Motor",
    "Masa Berlaku STNK Motor ke-1",
    "Masa Berlaku STNK Motor ke-2",
    "Masa Berlaku STNK Motor ke-3",
]
date_cols_present = [c for c in DATE_COLS if c in data.columns]

def highlight_expired(row):
    now = pd.Timestamp.now().normalize()
    for col in date_cols_present:
        dt = pd.to_datetime(row.get(col, pd.NaT), errors="coerce", dayfirst=True)
        if pd.notnull(dt) and dt < now:
            return ["background-color:#ffcccc; color:red; font-weight:bold"] * len(row)
    return [""] * len(row)

# ===== Kolom yang dicari =====
searchable_cols = []
if "NIK" in data.columns: searchable_cols.append("NIK")
name_cols = [c for c in data.columns if re.search(r"\bnama\b", c, flags=re.IGNORECASE)]
if name_cols: searchable_cols.append(name_cols[0])
plate_cols = [c for c in data.columns if ("No.Plat" in c) or ("No. Plat" in c) or ("Plat " in c)]
searchable_cols += plate_cols

# ===== Form Card (tanpa st.form agar tidak ada teks 'Press Enter...') =====
st.markdown('<div class="k-card">', unsafe_allow_html=True)
query = st.text_input("Masukkan Nama, NIK, atau No.Plat Kendaraan:", key="q", label_visibility="visible")
# beri kelas khusus ke input
st.markdown("""
<script>
const boxes=document.querySelectorAll('input[type="text"]');
boxes.forEach(b=>{ b.parentElement.parentElement.classList.add('k-input'); });
</script>
""", unsafe_allow_html=True)
submit = st.button("🔍 Cari Data")
st.markdown("</div>", unsafe_allow_html=True)

# ===== Search logic =====
if submit:
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
            st.success(f"Ditemukan {len(results)} hasil untuk '{q}'")
            st.dataframe(results.style.apply(highlight_expired, axis=1), use_container_width=True)
        else:
            st.markdown(f'<div class="info-banner">Tidak ditemukan hasil untuk "{q}".</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="info-banner">Silakan masukkan kata kunci untuk mencari data kendaraan.</div>', unsafe_allow_html=True)