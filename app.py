import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# ============ HEADER ============ #
st.set_page_config(page_title="Prediksi Status Mahasiswa", layout="centered")

# Gambar header
st.image("https://cdni.iconscout.com/illustration/premium/thumb/business-prediction-4380422-3653652.png", width=680)

st.title("Aplikasi Prediksi Status Mahasiswa")
st.markdown("""
Aplikasi ini menggunakan model machine learning untuk memprediksi status akhir mahasiswa:
**Dropout**, **Enrolled**, atau **Graduate**, berdasarkan data akademik dan administratif mereka.
""")
st.markdown("---")

# ==== Load model dan scaler dengan pengecekan path ====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "model/final_rf_model.pkl")
scaler_path = os.path.join(BASE_DIR, "model/scaler.pkl")

# Periksa apakah file ada sebelum load
if not os.path.exists(model_path):
    st.error("❌ File model tidak ditemukan: final_rf_model.pkl")
    st.stop()

if not os.path.exists(scaler_path):
    st.error("❌ File scaler tidak ditemukan: scaler.pkl")
    st.stop()

# Load model dan scaler
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

# ==== Panduan Konversi IPK ke Skala 20 ====
#st.markdown("### ℹ️ Panduan Konversi Nilai IPK ke Skala 0–20")
#ipk_values = np.arange(0.0, 4.1, 0.5)
#converted_values = ipk_values * 5
#ipk_table = pd.DataFrame({
#    "IPK (Skala 0–4)": ipk_values,
#    "Nilai Skala 0–20": converted_values
#})
#st.dataframe(ipk_table.style.format(precision=1), use_container_width=True)

# ==== Form Input ====
st.header("📋 Form Input Data Mahasiswa")

with st.form("form_mahasiswa"):
    st.subheader("📚 Nilai dan Riwayat Akademik")

    admission_grade = st.number_input("Nilai Penerimaan Mahasiswa", min_value=0.0, max_value=200.0, value=150.0)
    st.caption("Skala 0–200. Diambil dari nilai ujian masuk atau seleksi administrasi.")

    previous_grade = st.number_input("Nilai Pendidikan Sebelumnya", min_value=0.0, max_value=200.0, value=140.0)
    st.caption("Skala 0–200. Biasanya dari nilai sekolah menengah atau institusi sebelumnya.")

    age = st.number_input("Usia Saat Pendaftaran", min_value=15, max_value=60, value=20)
    st.caption("Masukkan usia saat mahasiswa diterima di universitas.")

    st.subheader("👤 Data Personal & Administratif")

    gender = st.radio("Jenis Kelamin", ["Female", "Male"])
    debtor = st.radio("Memiliki Tunggakan?", ["Yes", "No"])
    scholarship = st.radio("Penerima Beasiswa?", ["Yes", "No"])
    tuition = st.radio("Pembayaran SPP Lancar?", ["Yes", "No"])
    st.caption("Jawaban ini mempengaruhi prediksi ketertinggalan atau kesulitan akademik.")

    st.subheader("📘 Aktivitas Akademik Semester 1 & 2")

    cu1_enrolled = st.number_input("Jumlah Mata Kuliah Diambil (Semester 1)", min_value=0, max_value=30, value=6)
    cu1_approved = st.number_input("Jumlah Mata Kuliah Lulus (Semester 1)", min_value=0, max_value=30, value=5)

    cu1_grade = st.number_input("Rata-rata Nilai Semester 1 (Skala 0–20)", min_value=0.0, max_value=20.0, value=12.0)
    st.caption("Jika nilai Anda dalam skala 4 (IPK), kalikan dengan 5. Contoh: IPK 3.2 → 16.0")

    cu2_enrolled = st.number_input("Jumlah Mata Kuliah Diambil (Semester 2)", min_value=0, max_value=30, value=6)
    cu2_approved = st.number_input("Jumlah Mata Kuliah Lulus (Semester 2)", min_value=0, max_value=30, value=5)

    cu2_grade = st.number_input("Rata-rata Nilai Semester 2 (Skala 0–20)", min_value=0.0, max_value=20.0, value=12.0)
    st.caption("Jika nilai Anda dalam skala 4 (IPK), kalikan dengan 5. Contoh: IPK 3.0 → 15.0")

    # === Dropdown Bahasa Indonesia untuk Application Mode ===
    mode_options = {
        "Jalur Umum Tahap 1": 1,
        "Peraturan 612/93": 2,
        "Jalur Khusus Tahap 1 (Pulau Azores)": 5,
        "Pemegang Gelar Lainnya": 7,
        "Peraturan 854-B/99": 10,
        "Mahasiswa Internasional (S1)": 15,
        "Jalur Khusus Tahap 1 (Pulau Madeira)": 16,
        "Jalur Umum Tahap 2": 17,
        "Jalur Umum Tahap 3": 18,
        "Peraturan 533-A/99 (Rencana Berbeda)": 26,
        "Peraturan 533-A/99 (Institusi Lain)": 27,
        "Di Atas Usia 23 Tahun": 39,
        "Pindahan Antar Program": 42,
        "Ganti Program Studi": 43,
        "Lulusan Diploma Spesialisasi Teknologi": 44,
        "Ganti Institusi / Program": 51,
        "Lulusan Program Singkat": 53,
        "Ganti Institusi / Program (Internasional)": 57
    }

    selected_mode = st.selectbox("Jalur Masuk Mahasiswa", list(mode_options.keys()))
    application_mode = mode_options[selected_mode]
    st.caption("Pilih jalur masuk mahasiswa sesuai kebijakan institusi.")

    submitted = st.form_submit_button("🎯 Prediksi")

# ==== Prediksi jika form dikirim ====
if submitted:
    input_data = pd.DataFrame([{
        "Admission_grade": admission_grade,
        "Previous_qualification_grade": previous_grade,
        "Age_at_enrollment": age,
        "Gender": 1 if gender == "Female" else 0,
        "Debtor": 1 if debtor == "Yes" else 0,
        "Scholarship_holder": 1 if scholarship == "Yes" else 0,
        "Tuition_fees_up_to_date": 1 if tuition == "Yes" else 0,
        "Curricular_units_1st_sem_enrolled": cu1_enrolled,
        "Curricular_units_1st_sem_approved": cu1_approved,
        "Curricular_units_1st_sem_grade": cu1_grade,
        "Curricular_units_2nd_sem_enrolled": cu2_enrolled,
        "Curricular_units_2nd_sem_approved": cu2_approved,
        "Curricular_units_2nd_sem_grade": cu2_grade,
        "Application_mode": application_mode
    }])

    # ===== Manual One-Hot Encoding untuk Application_mode =====
    appmode_columns = ['AppMode_1', 'AppMode_2', 'AppMode_5', 'AppMode_7', 'AppMode_10', 'AppMode_15',
                       'AppMode_16', 'AppMode_17', 'AppMode_18', 'AppMode_26', 'AppMode_27', 'AppMode_39',
                       'AppMode_42', 'AppMode_43', 'AppMode_44', 'AppMode_51', 'AppMode_53', 'AppMode_57']

    for col in appmode_columns:
        input_data[col] = 0
    selected_col = f"AppMode_{application_mode}"
    if selected_col in appmode_columns:
        input_data[selected_col] = 1
    input_data.drop(columns=["Application_mode"], inplace=True)

    # ===== Prediksi =====
    input_scaled = scaler.transform(input_data)
    prediction = model.predict(input_scaled)[0]

    label_map = {0: "Dropout", 1: "Enrolled", 2: "Graduate"}
    status_label = label_map[prediction]
    st.success(f"Hasil Prediksi: **{status_label}**")

    # ===== Simpan ke CSV & Download Button =====
    input_data["Prediksi_Status"] = status_label
    csv = input_data.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="⬇️ Unduh Hasil Prediksi (CSV)",
        data=csv,
        file_name='prediksi_mahasiswa.csv',
        mime='text/csv'
    )

# ============ FOOTER ============ #
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 14px; color: grey;">
    📘 Dibuat oleh <b>abu_akhdan</b> &nbsp;|&nbsp; Dicoding Final Project <br>
    Data dari: <a href="https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success" target="_blank">UCI Machine Learning Repository</a> <br>
    © 2025
</div>
""", unsafe_allow_html=True)
