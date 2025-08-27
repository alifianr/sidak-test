import streamlit as st
import pandas as pd
from datetime import datetime

# ===== 💡 CSS Custom untuk Kalbe Style (langsung di sini, tidak perlu file CSS) =====
st.markdown("""
    <style>
        .stApp {
            background-color: #e8f5e9;
            color: #1b5e20;
        }

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
            background-color: #c8e6c9 !important;
            color: #1b5e20 !important;
            font-weight: bold;
            font-size: 16px;
            border-radius: 8px;
            padding: 0.5em 1em;
        }

        .stAlert-warning {
            background-color: #fff3cd !important;
            color: #795548 !important;
        }

        .stAlert-info {
            background-color: #d0f0fd !important;
            color: #0277bd !important;
        }

        h1, h2, h3, h4, h5 {
            color: #1b5e20;
            font-weight: 800;
            text-align: center;
        }

        .stDataFrame {
            background-color: #ffffff;
            color: #000000;
        }

        /* ✅ Tombol submit styling */
        div.stButton > button,
        button[aria-label="🔍 Cari Data"] {
            background-color: #1b5e20 !important;
            color: white !important;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            padding: 0.5em 1.5em;
            transition: 0.3s ease;
        }

        div.stButton > button[kind="primary"]:hover,
            div.stButton > button[aria-label="🔍 Cari Data"]:hover {
            background-color: #2e7d32 !important;
            color: white !important;
        }
        
        .st-cr {
            background-color: red;
            }

        .stAlertContainer {
            background-color: black;}

    </style>
""", unsafe_allow_html=True)

# ===== 🖼️ Logo Kalbe =====
st.image("kalbe.png", width=200)

# ===== 🧾 Judul Utama =====
st.title("🔍 Pencarian Data Kendaraan")
st.markdown("<h4 style='text-align: center;'>PT Kalbe Morinaga Indonesia</h4>", unsafe_allow_html=True)

# ===== 📦 Load Data =====
data = pd.read_csv('data_kendaraan.csv')
data.columns = data.columns.str.strip()  # hapus spasi di nama kolom

# ===== 🎨 Highlight baris kadaluarsa =====
def highlight_expired(row):
    now = pd.Timestamp.now()
    sim_date = pd.to_datetime(row['Masa Berlaku SIM'], errors='coerce')
    stnk_date = pd.to_datetime(row['Masa Berlaku STNK'], errors='coerce')

    sim_expired = sim_date < now if pd.notnull(sim_date) else False
    stnk_expired = stnk_date < now if pd.notnull(stnk_date) else False

    if sim_expired or stnk_expired:
        return ['background-color: #ffcccc; color: red; font-weight: bold'] * len(row)
    else:
        return [''] * len(row)

# ===== 🔍 Form Pencarian =====
with st.form("form_pencarian"):
    query = st.text_input("Masukkan Nama, NIK, atau No.Plat Kendaraan:")
    submit = st.form_submit_button("🔍 Cari Data")

# ===== 🔎 Proses Pencarian =====
if submit:
    results = data[
        (data['Nama Lengkap'].astype(str).str.contains(query, case=False, na=False)) |
        (data['NIK'].astype(str).str.contains(query, case=False, na=False)) |
        (data['No.Plat'].astype(str).str.contains(query, case=False, na=False))
    ]
    
    if not results.empty:
        st.success(f"Ditemukan {len(results)} hasil untuk '{query}'")
        styled = results.style.apply(highlight_expired, axis=1)
        st.dataframe(styled, use_container_width=True)
    else:
        st.warning(f"Tidak ditemukan hasil untuk '{query}'")
elif query == "":
    st.info("Silakan masukkan kata kunci untuk mencari data kendaraan.")
