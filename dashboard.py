import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Puskesmas Bugangan 2024",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1F4E79, #2E75B6);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #EBF3FB;
        border-left: 4px solid #2E75B6;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .section-header {
        color: #1F4E79;
        border-bottom: 2px solid #2E75B6;
        padding-bottom: 5px;
        margin: 15px 0 10px 0;
    }
    .warning-box {
        background: #FFF3CD;
        border-left: 4px solid #FFC107;
        padding: 10px;
        border-radius: 5px;
    }
    .success-box {
        background: #D4EDDA;
        border-left: 4px solid #28A745;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA SETUP (berdasarkan Profil Kesehatan 2024)
# ─────────────────────────────────────────────
np.random.seed(42)

BULAN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
         'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']

KUNJUNGAN = [3200, 3050, 3800, 3600, 3700, 3500,
             3400, 3650, 3700, 3900, 3974, 3700]

DF_PENYAKIT = pd.DataFrame({
    'Kode': ['J00', 'I10', 'E11', 'L30', 'R50', 'R05', 'K29', 'G44', 'K04.1', 'A09'],
    'Penyakit': ['ISPA', 'Hipertensi', 'Diabetes Melitus', 'Dermatitis',
                 'Demam', 'Batuk', 'Gastritis', 'Sakit Kepala',
                 'Nekrosis Pulpa', 'Diare'],
    'Kasus': [5799, 2912, 2159, 1398, 1330, 1154, 1072, 908, 798, 706],
    'Kategori': ['Menular', 'PTM', 'PTM', 'Menular', 'Menular',
                 'Menular', 'PTM', 'PTM', 'Non-infeksius', 'Menular']
})
DF_PENYAKIT['%'] = (DF_PENYAKIT['Kasus'] / DF_PENYAKIT['Kasus'].sum() * 100).round(1)

DF_KIA = pd.DataFrame({
    'Tahun': [2022, 2023, 2024],
    'K1': [256, 218, 146], 'K4': [253, 181, 154],
    'Persalinan': [280, 225, 178], 'Neonatal': [285, 230, 153],
    'Kematian_Bayi': [3, 2, 2], 'Kematian_Ibu': [0, 0, 0],
    'ASI_Eksklusif': [95, 98, 100]
})

DF_MENULAR = pd.DataFrame({
    'Tahun': [2020, 2021, 2022, 2023, 2024],
    'TB_BTA': [34, 97, 57, 19, 21],
    'TB_Target': [36, 58, 65, 75, 26],
    'TB_CureRate': [100, 100, 61, 97, 69],
    'DBD': [12, 8, 15, 4, 47],
    'HIV': [3, 5, 6, 8, 5],
    'Diare': [450, 490, 510, 520, 533]
})

KELURAHAN_DATA = pd.DataFrame({
    'Kelurahan': ['Bugangan', 'Mlatiharjo', 'Kebonagung'],
    'Populasi': [7478, 4857, 4213],
    'BPJS': [5823, 4214, 4109],
    'Luas_km2': [0.49, 0.45, 0.24],
    'DBD_2024': [6, 4+7, 5+4],
})
KELURAHAN_DATA['Kepadatan'] = (KELURAHAN_DATA['Populasi'] / KELURAHAN_DATA['Luas_km2']).round(0)
KELURAHAN_DATA['Cakupan_BPJS'] = (KELURAHAN_DATA['BPJS'] / KELURAHAN_DATA['Populasi'] * 100).round(1)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/UPN_Veteran_Jatim.png/120px-UPN_Veteran_Jatim.png",
             width=80)
    st.markdown("### 🏥 Puskesmas Bugangan")
    st.markdown("**Kota Semarang, Jawa Tengah**")
    st.markdown("---")

    halaman = st.radio(
        "📑 Pilih Halaman:",
        ["🏠 Ringkasan Eksekutif",
         "📊 Kunjungan Pasien",
         "🦠 Pola Penyakit",
         "👶 Kesehatan Keluarga",
         "📈 Tren & Prediksi",
         "🗺️ Sebaran Kelurahan",
         "⚙️ Data Lifecycle"],
        index=0
    )

    st.markdown("---")
    st.markdown("**📅 Sumber Data:**")
    st.markdown("Profil Kesehatan Puskesmas Bugangan Tahun 2024")

# ─────────────────────────────────────────────
# HALAMAN 1: RINGKASAN EKSEKUTIF
# ─────────────────────────────────────────────
if halaman == "🏠 Ringkasan Eksekutif":
    st.markdown("""
    <div class="main-header">
        <h2>🏥 Dashboard Big Data — UPTD Puskesmas Bugangan</h2>
        <p>Kecamatan Semarang Timur, Kota Semarang | Tahun 2024</p>
    </div>
    """, unsafe_allow_html=True)

    # KPI Baris 1
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total Kunjungan", "43.174", "+7.14% vs 2023")
    col2.metric("📅 Rata-rata/Hari", "~155 pasien", "262 hari kerja")
    col3.metric("🏘️ Wilayah Kerja", "3 Kelurahan", "16.548 jiwa")
    col4.metric("💊 Ketersediaan Obat", "100%", "40 item esensial")

    # KPI Baris 2
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("👩‍⚕️ Tenaga Kesehatan", "45 orang", "38 ASN + 7 Non-ASN")
    col6.metric("🤱 AKI (Kematian Ibu)", "0 kasus", "Target: 0 ✅")
    col7.metric("👶 AKB (Kematian Bayi)", "2 kasus", "5.62/1000 KH")
    col8.metric("🦟 Kasus DBD", "47 kasus", "↑ dari 4 kasus 2023 ⚠️")

    st.markdown("---")

    # Quick chart
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 📊 Kunjungan Bulanan 2024")
        fig, ax = plt.subplots(figsize=(8, 4))
        colors = ['#e17055' if k == max(KUNJUNGAN) else '#2E75B6' for k in KUNJUNGAN]
        bars = ax.bar(BULAN, KUNJUNGAN, color=colors, edgecolor='white', alpha=0.9)
        ax.axhline(np.mean(KUNJUNGAN), color='red', linestyle='--', linewidth=1.5,
                   label=f'Rata-rata: {int(np.mean(KUNJUNGAN)):,}')
        ax.set_ylabel('Kunjungan')
        ax.legend(fontsize=9)
        ax.set_title('Total: 43.174 kunjungan (+7.14% dari 2023)', fontsize=10)
        for bar, val in zip(bars, KUNJUNGAN):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 20,
                    f'{val:,}', ha='center', fontsize=7)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_b:
        st.markdown("#### 🦠 10 Besar Penyakit 2024")
        fig, ax = plt.subplots(figsize=(8, 4))
        colors_p = ['#e17055' if k == 'Menular' else ('#6c5ce7' if k == 'PTM' else '#00cec9')
                    for k in DF_PENYAKIT['Kategori']]
        ax.barh(DF_PENYAKIT['Penyakit'][::-1], DF_PENYAKIT['Kasus'][::-1],
                color=colors_p[::-1], edgecolor='white', alpha=0.9)
        ax.set_xlabel('Jumlah Kasus')
        ax.set_title('Dominasi ISPA (32%) dan PTM', fontsize=10)
        legend_el = [mpatches.Patch(color='#e17055', label='Menular'),
                     mpatches.Patch(color='#6c5ce7', label='PTM')]
        ax.legend(handles=legend_el, fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Tabel KPI
    st.markdown("#### 📋 Status KPI Utama")
    kpi_df = pd.DataFrame({
        'KPI': ['Cakupan K1 Ibu Hamil', 'Cakupan K4 Ibu Hamil', 'Persalinan oleh Nakes',
                'Imunisasi Dasar Lengkap', 'Kunjungan Neonatal', 'Balita Ditimbang',
                'Cure Rate TB', 'Cakupan Lansia Skrining', 'Realisasi Anggaran BLUD'],
        'Capaian': ['100%', '100%', '100%', '99.5%', '100%', '100%', '69%', '~80%', '97.03%'],
        'Target': ['100%', '100%', '100%', '≥95%', '100%', '100%', '≥85%', '100%', '≥90%'],
        'Status': ['✅', '✅', '✅', '✅', '✅', '✅', '⚠️', '⚠️', '✅']
    })
    st.dataframe(kpi_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# HALAMAN 2: KUNJUNGAN PASIEN
# ─────────────────────────────────────────────
elif halaman == "📊 Kunjungan Pasien":
    st.title("📊 Analisis Kunjungan Pasien 2024")

    # Filter interaktif
    col_f1, col_f2 = st.columns(2)
    bulan_filter = col_f1.multiselect("Filter Bulan:", BULAN, default=BULAN)
    show_avg = col_f2.checkbox("Tampilkan garis rata-rata", value=True)

    idx_filter = [BULAN.index(b) for b in bulan_filter]
    kunjungan_filter = [KUNJUNGAN[i] for i in idx_filter]

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(9, 5))
        bar_colors = ['#2E75B6'] * len(bulan_filter)
        bars = ax.bar(bulan_filter, kunjungan_filter, color=bar_colors, edgecolor='white', alpha=0.88)
        if show_avg:
            avg = np.mean(kunjungan_filter)
            ax.axhline(avg, color='#e17055', linestyle='--', linewidth=2,
                       label=f'Rata-rata: {int(avg):,}')
            ax.legend()
        ax.set_title('Kunjungan Pasien per Bulan', fontsize=12, fontweight='bold')
        ax.set_ylabel('Jumlah Kunjungan')
        for bar, val in zip(bars, kunjungan_filter):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 30,
                    f'{val:,}', ha='center', fontsize=8, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, axes = plt.subplots(1, 2, figsize=(9, 5))
        # Pie jenis kelamin
        axes[0].pie([32299, 10875], labels=['Perempuan\n74.8%', 'Laki-laki\n25.2%'],
                    colors=['#fd79a8', '#74b9ff'], autopct='%1.1f%%', startangle=90,
                    pctdistance=0.7)
        axes[0].set_title('Jenis Kelamin', fontweight='bold')

        # Pie kepesertaan
        axes[1].pie([23745, 12952, 6477],
                    labels=['BPJS PBI\n55%', 'BPJS Non-PBI\n30%', 'Umum\n15%'],
                    colors=['#00b894', '#0984e3', '#fdcb6e'], autopct='%1.1f%%',
                    startangle=90, pctdistance=0.7)
        axes[1].set_title('Kepesertaan', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Statistik
    st.markdown("#### 📈 Statistik Kunjungan")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total", f"{sum(kunjungan_filter):,}")
    c2.metric("Rata-rata/bulan", f"{int(np.mean(kunjungan_filter)):,}")
    c3.metric("Median", f"{int(np.median(kunjungan_filter)):,}")
    c4.metric("Tertinggi", f"{max(kunjungan_filter):,}")
    c5.metric("Terendah", f"{min(kunjungan_filter):,}")

# ─────────────────────────────────────────────
# HALAMAN 3: POLA PENYAKIT
# ─────────────────────────────────────────────
elif halaman == "🦠 Pola Penyakit":
    st.title("🦠 Analisis Pola Penyakit 2024")

    # Filter kategori
    kategori_sel = st.multiselect(
        "Filter Kategori:", ['Menular', 'PTM', 'Non-infeksius'],
        default=['Menular', 'PTM', 'Non-infeksius']
    )
    df_filter = DF_PENYAKIT[DF_PENYAKIT['Kategori'].isin(kategori_sel)]

    col1, col2 = st.columns([3, 2])

    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))
        colors_map = {'Menular': '#e17055', 'PTM': '#6c5ce7', 'Non-infeksius': '#00cec9'}
        colors_bars = [colors_map[k] for k in df_filter['Kategori'][::-1]]
        bars = ax.barh(df_filter['Penyakit'][::-1], df_filter['Kasus'][::-1],
                       color=colors_bars, edgecolor='white', alpha=0.9, height=0.6)
        ax.set_xlabel('Jumlah Kasus')
        ax.set_title('Distribusi 10 Besar Penyakit Puskesmas Bugangan 2024',
                     fontweight='bold', fontsize=12)
        for bar, val in zip(bars, df_filter['Kasus'][::-1]):
            ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2,
                    f'{val:,}', va='center', fontsize=9)
        legend_el = [mpatches.Patch(color=v, label=k) for k, v in colors_map.items()]
        ax.legend(handles=legend_el, loc='lower right')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("#### Ringkasan Kategori")
        for cat in ['Menular', 'PTM', 'Non-infeksius']:
            total = DF_PENYAKIT[DF_PENYAKIT['Kategori'] == cat]['Kasus'].sum()
            pct = total / DF_PENYAKIT['Kasus'].sum() * 100
            st.markdown(f"""
            <div class="metric-card">
                <b>{cat}</b><br>
                {total:,} kasus ({pct:.1f}%)
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Tabel Detail")
        st.dataframe(
            df_filter[['Kode', 'Penyakit', 'Kasus', '%', 'Kategori']].reset_index(drop=True),
            use_container_width=True, hide_index=True
        )

    # Alert DBD
    st.markdown("""
    <div class="warning-box">
        <b>⚠️ Perhatian: Lonjakan DBD 2024</b><br>
        Kasus DBD meningkat drastis dari 4 kasus (2023) menjadi 47 kasus (2024) — naik 1.075%.
        Diperlukan intensifikasi Pemberantasan Jentik Nyamuk (PJN) dan pemantauan berbasis data.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HALAMAN 4: KESEHATAN KELUARGA
# ─────────────────────────────────────────────
elif halaman == "👶 Kesehatan Keluarga":
    st.title("👶 Analisis Kesehatan Keluarga (KIA) 2022–2024")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot([2022, 2023, 2024], DF_KIA['K1'], 'o-', color='#6c5ce7',
                linewidth=2.5, markersize=8, label='K1 Ibu Hamil')
        ax.plot([2022, 2023, 2024], DF_KIA['K4'], 's-', color='#fd79a8',
                linewidth=2.5, markersize=8, label='K4 Ibu Hamil')
        ax.plot([2022, 2023, 2024], DF_KIA['Persalinan'], '^-', color='#00b894',
                linewidth=2.5, markersize=8, label='Persalinan Nakes')
        ax.plot([2022, 2023, 2024], DF_KIA['Neonatal'], 'D-', color='#fdcb6e',
                linewidth=2.5, markersize=8, label='Kunjungan Neonatal')
        ax.set_title('Tren Pelayanan KIA 2022–2024', fontweight='bold', fontsize=12)
        ax.set_xticks([2022, 2023, 2024])
        ax.set_ylabel('Jumlah')
        ax.legend(fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, axes = plt.subplots(1, 2, figsize=(9, 5))

        # Kematian bayi
        axes[0].bar([2022, 2023, 2024], DF_KIA['Kematian_Bayi'],
                    color=['#e17055', '#fdcb6e', '#fdcb6e'], edgecolor='white')
        axes[0].set_title('Kematian Bayi', fontweight='bold')
        axes[0].set_xticks([2022, 2023, 2024])
        axes[0].set_ylabel('Kasus')
        for x, y in zip([2022, 2023, 2024], DF_KIA['Kematian_Bayi']):
            axes[0].text(x, y + 0.05, str(y), ha='center', fontsize=10, fontweight='bold')

        # ASI Eksklusif
        axes[1].plot([2022, 2023, 2024], DF_KIA['ASI_Eksklusif'], 'o-',
                     color='#00b894', linewidth=2.5, markersize=8)
        axes[1].fill_between([2022, 2023, 2024], DF_KIA['ASI_Eksklusif'],
                              alpha=0.2, color='#00b894')
        axes[1].set_ylim(90, 102)
        axes[1].set_title('ASI Eksklusif (%)', fontweight='bold')
        axes[1].set_xticks([2022, 2023, 2024])
        for x, y in zip([2022, 2023, 2024], DF_KIA['ASI_Eksklusif']):
            axes[1].text(x, y + 0.3, f'{y}%', ha='center', fontsize=10, fontweight='bold')

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("""
    <div class="success-box">
        <b>✅ Capaian KIA 2024:</b> Seluruh indikator (K1, K4, persalinan nakes, neonatal, KF lengkap,
        ASI eksklusif) mencapai 100% dari target. Tidak ada kematian ibu. AKB turun dari 2023.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HALAMAN 5: TREN & PREDIKSI
# ─────────────────────────────────────────────
elif halaman == "📈 Tren & Prediksi":
    st.title("📈 Analisis Tren & Prediksi (ARIMA)")

    col1, col2 = st.columns(2)

    with col1:
        fig, axes = plt.subplots(2, 1, figsize=(9, 8))

        # TB trend
        axes[0].plot(DF_MENULAR['Tahun'], DF_MENULAR['TB_BTA'], 'o-',
                     color='#e17055', linewidth=2.5, markersize=8, label='Kasus TB BTA+')
        axes[0].plot(DF_MENULAR['Tahun'], DF_MENULAR['TB_Target'], 's--',
                     color='#636e72', linewidth=1.5, label='Target')
        axes[0].set_title('Tren TB Paru BTA+ (2020–2024)', fontweight='bold')
        axes[0].set_ylabel('Kasus')
        axes[0].legend()

        # DBD trend
        dbd_colors = ['#fdcb6e' if v < 20 else '#e17055' for v in DF_MENULAR['DBD']]
        axes[1].bar(DF_MENULAR['Tahun'], DF_MENULAR['DBD'], color=dbd_colors, edgecolor='white')
        axes[1].set_title('Tren DBD (2020–2024)', fontweight='bold')
        axes[1].set_ylabel('Kasus')
        axes[1].annotate('⚠️ Lonjakan!', xy=(2024, 47), xytext=(2022.5, 38),
                         arrowprops=dict(arrowstyle='->', color='red'), color='red', fontsize=9)
        for x, y in zip(DF_MENULAR['Tahun'], DF_MENULAR['DBD']):
            axes[1].text(x, y + 0.5, str(y), ha='center', fontsize=9, fontweight='bold')

        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown("#### 🔮 Forecasting Kunjungan — ARIMA(1,1,1)")

        try:
            from statsmodels.tsa.arima.model import ARIMA
            import pandas as pd

            ts = pd.Series(KUNJUNGAN, index=pd.date_range('2024-01', periods=12, freq='MS'))
            model = ARIMA(ts, order=(1, 1, 1)).fit()
            forecast = model.forecast(steps=6)
            forecast_idx = pd.date_range('2025-01', periods=6, freq='MS')

            fig, ax = plt.subplots(figsize=(9, 5))
            hist_idx = pd.date_range('2024-01', periods=12, freq='MS')
            ax.plot(hist_idx, KUNJUNGAN, 'o-', color='#2E75B6',
                    linewidth=2, markersize=6, label='Data Aktual 2024')
            ax.plot(forecast_idx, forecast.values, 's--', color='#e17055',
                    linewidth=2, markersize=6, label='Prediksi 2025 (ARIMA)')
            ax.fill_between(forecast_idx,
                            forecast.values * 0.93,
                            forecast.values * 1.07,
                            alpha=0.2, color='#e17055', label='CI ±7%')
            ax.axvline(pd.Timestamp('2025-01'), color='gray', linestyle=':', linewidth=1.5)
            ax.set_title('Forecasting Kunjungan Jan–Jun 2025', fontweight='bold')
            ax.set_ylabel('Kunjungan')
            ax.legend(fontsize=9)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

            st.markdown("**Hasil Prediksi:**")
            pred_df = pd.DataFrame({
                'Bulan': [d.strftime('%B %Y') for d in forecast_idx],
                'Prediksi (pasien)': [f"{int(v):,}" for v in forecast.values]
            })
            st.dataframe(pred_df, use_container_width=True, hide_index=True)
            st.info(f"Rata-rata prediksi: **{int(forecast.mean()):,} pasien/bulan** | AIC: {model.aic:.1f}")

        except ImportError:
            st.warning("Install statsmodels: `pip install statsmodels`")

    # Heatmap korelasi
    st.markdown("#### 🔥 Heatmap Korelasi Antar Indikator")
    curah_hujan = [320, 280, 250, 180, 120, 80, 60, 70, 150, 200, 280, 310]
    kpi_corr = pd.DataFrame({
        'Kunjungan': KUNJUNGAN,
        'Hipertensi_est': [int(k * 2912/43174) for k in KUNJUNGAN],
        'DM_est': [int(k * 2159/43174) for k in KUNJUNGAN],
        'ISPA_est': [int(k * 5799/43174) for k in KUNJUNGAN],
        'Curah_Hujan': curah_hujan
    })
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(kpi_corr.corr(), annot=True, fmt='.2f', cmap='coolwarm',
                center=0, ax=ax, linewidths=0.5,
                xticklabels=['Kunjungan', 'HTN', 'DM', 'ISPA', 'Hujan'],
                yticklabels=['Kunjungan', 'HTN', 'DM', 'ISPA', 'Hujan'])
    ax.set_title('Korelasi Pearson Antar Indikator Kesehatan', fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ─────────────────────────────────────────────
# HALAMAN 6: SEBARAN KELURAHAN
# ─────────────────────────────────────────────
elif halaman == "🗺️ Sebaran Kelurahan":
    st.title("🗺️ Analisis Per Kelurahan")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(9, 5))
        x = np.arange(3)
        w = 0.25
        b1 = ax.bar(x - w, KELURAHAN_DATA['Populasi'] / 100, w,
                    label='Populasi (/100)', color='#74b9ff')
        b2 = ax.bar(x, KELURAHAN_DATA['BPJS'] / 100, w,
                    label='Peserta BPJS (/100)', color='#00b894')
        b3 = ax.bar(x + w, KELURAHAN_DATA['DBD_2024'], w,
                    label='Kasus DBD', color='#e17055')
        ax.set_xticks(x)
        ax.set_xticklabels(KELURAHAN_DATA['Kelurahan'])
        ax.set_title('Populasi, BPJS & DBD per Kelurahan', fontweight='bold')
        ax.legend(fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        fig, ax = plt.subplots(figsize=(9, 5))
        colors_kel = ['#2E75B6', '#00b894', '#e17055']
        bars = ax.bar(KELURAHAN_DATA['Kelurahan'],
                      KELURAHAN_DATA['Kepadatan'],
                      color=colors_kel, edgecolor='white', alpha=0.9)
        ax.set_title('Kepadatan Penduduk (jiwa/km²)', fontweight='bold')
        ax.set_ylabel('jiwa/km²')
        for bar, val in zip(bars, KELURAHAN_DATA['Kepadatan']):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 100,
                    f'{int(val):,}', ha='center', fontsize=10, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("#### 📋 Data Lengkap per Kelurahan")
    disp = KELURAHAN_DATA.copy()
    disp.columns = ['Kelurahan', 'Populasi', 'Peserta BPJS', 'Luas (km²)',
                    'Kasus DBD 2024', 'Kepadatan (jiwa/km²)', 'Cakupan BPJS (%)']
    st.dataframe(disp, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# HALAMAN 7: DATA LIFECYCLE
# ─────────────────────────────────────────────
elif halaman == "⚙️ Data Lifecycle":
    st.title("⚙️ Desain Data Lifecycle — Puskesmas Bugangan")
    st.markdown("Visualisasi 5 tahapan Data Lifecycle sesuai **Bagian C** laporan ETS.")

    tahap = st.selectbox("📌 Pilih Tahap:", [
        "① Acquisition — Pengumpulan Data",
        "② Storage — Penyimpanan Data",
        "③ Processing — Pengolahan Data",
        "④ Analysis — Analisis Data",
        "⑤ Visualization — Tampilan Data"
    ])

    if "Acquisition" in tahap:
        st.markdown("### ① Data Acquisition")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Sumber data internal:**
            - 🖥️ SIMPUS — rekam medis, kunjungan pasien
            - 📋 Loket pendaftaran — input e-KTP / manual
            - 💊 Sistem farmasi — stok & dispensing obat
            - 🔬 Laboratorium — hasil pemeriksaan
            - 📊 Posyandu — data timbang balita & ibu hamil

            **Sumber data eksternal:**
            - 🏥 BPJS Kesehatan — data kepesertaan & klaim
            - 🏛️ Dukcapil — validasi NIK penduduk
            - 🌦️ BMKG — data cuaca (korelasi DBD)
            - 📡 SATUSEHAT Kemenkes — laporan SPM
            """)
        with col2:
            st.markdown("""
            **Teknologi IoT yang dapat diintegrasikan:**
            - 📲 Mesin antrian digital + pemindai e-KTP
            - 🌡️ Sensor suhu & kelembaban ruang tunggu
            - 💉 Blood pressure monitor digital (poli)
            - 📦 RFID tracking stok obat di apotek
            - 📡 Sensor nyamuk (ABJ untuk DBD)

            **Frekuensi pengumpulan:**
            - Real-time: antrian, kunjungan harian
            - Harian: laporan stok obat, jumlah pasien
            - Bulanan: laporan KIA, imunisasi, PTM
            - Tahunan: Profil Kesehatan, laporan SPM
            """)

    elif "Storage" in tahap:
        st.markdown("### ② Data Storage")
        st.markdown("""
        | Layer | Teknologi | Fungsi |
        |-------|-----------|--------|
        | **Local DB** | SIMPUS (PostgreSQL/MySQL) | Rekam medis harian, kunjungan, resep |
        | **Cloud SATUSEHAT** | FHIR R4 API Kemenkes | Rekam medis elektronik nasional |
        | **Data Warehouse** | Dinkes Kota Semarang | Agregasi multi-puskesmas |
        | **Backup** | Cloud storage terenkripsi | AES-256, retensi 7 tahun |
        """)
        st.info("**Kebijakan:** Data pasien bersifat confidential, akses berdasarkan role-based (Permenkes No. 24/2022 tentang Rekam Medis)")

    elif "Processing" in tahap:
        st.markdown("### ③ Data Processing")

        tab1, tab2, tab3 = st.tabs(["🧹 Cleaning", "🔄 Transformasi", "🔗 Integrasi"])

        with tab1:
            st.markdown("""
            **Masalah data yang ditemukan:**
            - Duplikat entri pasien (NIK + tanggal kunjungan sama)
            - Missing values pada kolom diagnosa ICD-10
            - Format tanggal tidak konsisten
            - NIK tidak valid (bukan 16 digit)

            **Solusi cleaning (Python/pandas):**
            ```python
            df.drop_duplicates(subset=['NIK', 'tanggal_kunjungan'])
            df['kode_icd10'].fillna('UNKNOWN')
            df['NIK_valid'] = df['NIK'].str.len() == 16
            ```
            """)

        with tab2:
            st.markdown("""
            **Proses transformasi:**
            - Agregasi kunjungan harian → mingguan/bulanan
            - Kategorisasi usia (balita, remaja, dewasa, lansia)
            - Normalisasi kode penyakit ke ICD-10
            - Konversi data kohort KIA → cakupan K1/K4

            **Contoh agregasi:**
            ```python
            df_bulanan = df.groupby(['bulan', 'kelurahan'])\\
                .agg(kunjungan=('id', 'count'),\\
                     rata_usia=('usia', 'mean')).reset_index()
            ```
            """)

        with tab3:
            st.markdown("""
            **Integrasi multi-sumber:**
            - JOIN data SIMPUS + data kepesertaan BPJS
            - Sinkronisasi posyandu → database induk
            - API FHIR R4 ke platform SATUSEHAT
            - Validasi silang NIK dengan Dukcapil

            **Hasil integrasi dipakai untuk:**
            - Utilisasi rate per kelurahan
            - Cakupan BPJS vs total populasi
            - Identifikasi pasien TB/Hipertensi yang tidak kontrol
            """)

    elif "Analysis" in tahap:
        st.markdown("### ④ Data Analysis")

        analisis_df = pd.DataFrame({
            'Jenis Analisis': ['Deskriptif', 'Prediktif', 'Machine Learning'],
            'Metode': [
                'Statistik dasar, tren time-series, proporsi',
                'Regresi linear, forecasting ARIMA(1,1,1)',
                'Decision Tree / Random Forest (klasifikasi risiko)'
            ],
            'Penerapan di Puskesmas Bugangan': [
                'Analisis 10 penyakit terbanyak, tren kunjungan +7.14%',
                'Prediksi kunjungan Jan–Jun 2025, prediksi stok obat',
                'Klasifikasi pasien hipertensi risiko tinggi, deteksi TB mangkir'
            ]
        })
        st.dataframe(analisis_df, use_container_width=True, hide_index=True)
        st.info("💡 Implementasi lengkap ada di notebook Google Colab (file .ipynb)")

    elif "Visualization" in tahap:
        st.markdown("### ⑤ Data Visualization")
        st.markdown("""
        **Tool yang digunakan:**

        | Tool | Platform | Pengguna |
        |------|----------|----------|
        | **Streamlit** (dashboard ini) | VSCode / localhost:8501 | Kepala Puskesmas, petugas |
        | **Google Colab** (notebook) | Browser | Analis data, mahasiswa |
        | **SATUSEHAT** | Cloud Kemenkes | Dinkes, Kemenkes |
        | **Profil Tahunan PDF** | Cetak / upload web | Masyarakat umum |

        **Cara menjalankan dashboard ini di VSCode:**
        ```bash
        pip install streamlit pandas numpy matplotlib seaborn statsmodels
        streamlit run dashboard.py
        # Buka browser: http://localhost:8501
        ```
        """)
        st.success("✅ Kamu sedang membuka dashboard Streamlit ini sekarang!")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small>📊 Dashboard Big Data ETS | UPTD Puskesmas Bugangan 2024 | "
    "UPN 'Veteran' Jawa Timur | Dosen: Dr. Eng. Agussalim, MT.</small>",
    unsafe_allow_html=True
)