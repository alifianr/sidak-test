import streamlit as st
import pandas as pd

# ===== 💡 CSS Custom untuk Kalbe Style =====
st.markdown("""
    <style>
        /* 🌿 Warna dasar aplikasi */
        .stApp {
            background-color: #e8f5e9; /* hijau muda background */
            color: #1b5e20;           /* hijau tua sebagai warna teks utama */
        }

        /* 🏷️ Warna untuk label, judul, dan teks lainnya */
        label, .stTextInput label, .stTextInput > div > label,
        .stMarkdown, .stInfo, .stWarning {
            color: #1b5e20 !important;
            font-weight: bold;
        }

        /* 📝 Input Field */
        .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #1b5e20 !important;
            border: 1px solid #81c784;
            font-weight: bold;
        }

        /* ✅ st.success dan alert box styling */
        .stAlert-success {
            background-color: #c8e6c9 !important;
            color: #1b5e20 !important;
            font-weight: bold;
            font-size: 16px;
        }

        .stAlert-warning {
            background-color: #fff3cd !important;
            color: #795548 !important;
        }

        .stAlert-info {
            background-color: #d0f0fd !important;
            color: #0277bd !important;
        }

        /* 🎯 Judul dan heading */
        h1, h2, h3, h4, h5 {
            color: #1b5e20;
            font-weight: 800;
            text-align: center;
        }

        /* 💬 DataFrame dan hasil pencarian */
        .stDataFrame {
            background-color: #ffffff;
            color: #000000;
        }
    </style>
""", unsafe_allow_html=True)


# ===== 🖼️ Tampilkan Logo Kalbe =====
st.image("kalbe.png", width=200)

# ===== 📘 Judul Utama =====
st.title("🔍 Pencarian Data Kendaraan")
st.markdown("<h4 style='text-align: center;'>PT Kalbe Morinaga Indonesia</h4>", unsafe_allow_html=True)

# ===== 📦 Load data =====
data = pd.read_csv('data_kendaraan.csv')

# ===== 🔍 Form Pencarian =====
query = st.text_input("Masukkan Nama, NIK, atau No.Plat Kendaraan:")

if query:
    results = data[
        (data['Nama Lengkap'].astype(str).str.contains(query, case=False, na=False)) |
        (data['NIK'].astype(str).str.contains(query, case=False, na=False)) |
        (data['No.Plat'].astype(str).str.contains(query, case=False, na=False))
    ]
    
    if not results.empty:
        st.success(f"Ditemukan {len(results)} hasil untuk '{query}'")
        st.dataframe(results)
    else:
        st.warning(f"Tidak ditemukan hasil untuk '{query}'")
else:
    st.info("Silakan masukkan kata kunci untuk mencari data kendaraan.")
