"""
app.py — Cloud Forensics Automation for Manufacturing Breaches
Advanced UI Edition — Streamlit
"""

import io
import os
import streamlit as st
import pandas as pd

from utils import scan_directory, scan_uploaded_files, compute_metrics

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cloud Forensics | Manufacturing",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Advanced CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #020617 0%, #0a0f1e 40%, #0d1b2a 100%);
    min-height: 100vh;
}

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #050d1a 0%, #0a1628 60%, #0d1f38 100%) !important;
    border-right: 1px solid rgba(56, 189, 248, 0.15) !important;
}
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #38bdf8 !important; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(14,26,46,0.9), rgba(10,16,30,0.95)) !important;
    border: 1px solid rgba(56,189,248,0.2) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(12px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(56,189,248,0.15) !important;
}
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 12px !important; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-size: 30px !important; font-weight: 800 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 20px rgba(14,165,233,0.35) !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(14,165,233,0.5) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(56,189,248,0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.15) !important;
}

/* ── Radio ── */
.stRadio > div { gap: 8px; }
.stRadio label { color: #94a3b8 !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(56,189,248,0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 11px 24px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 16px rgba(16,185,129,0.3) !important;
    transition: all 0.25s ease !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(16,185,129,0.45) !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(56,189,248,0.12) !important;
}

/* ── Custom cards ── */
.glass-card {
    background: linear-gradient(135deg, rgba(14,26,46,0.85), rgba(10,16,30,0.9));
    border: 1px solid rgba(56,189,248,0.18);
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    backdrop-filter: blur(16px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.info-box {
    background: linear-gradient(135deg, rgba(14, 74, 110, 0.5), rgba(12, 60, 90, 0.5));
    border-left: 3px solid #38bdf8;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 14px;
    color: #bae6fd;
    backdrop-filter: blur(8px);
}
.warn-box {
    background: linear-gradient(135deg, rgba(120,53,15,0.5), rgba(100,40,10,0.5));
    border-left: 3px solid #f59e0b;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 14px;
    color: #fde68a;
    backdrop-filter: blur(8px);
}
.success-box {
    background: linear-gradient(135deg, rgba(6,78,59,0.5), rgba(5,60,48,0.5));
    border-left: 3px solid #10b981;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 14px;
    color: #a7f3d0;
    backdrop-filter: blur(8px);
}

/* ── Hero section ── */
.hero {
    text-align: center;
    padding: 40px 20px 30px;
    position: relative;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(14,165,233,0.2), rgba(99,102,241,0.2));
    border: 1px solid rgba(99,102,241,0.4);
    color: #a5b4fc;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 100px;
    margin-bottom: 16px;
}
.hero-title {
    font-size: 52px;
    font-weight: 800;
    background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin: 8px 0;
}
.hero-sub {
    color: #64748b;
    font-size: 17px;
    font-weight: 400;
    margin: 10px 0 0;
    letter-spacing: 0.3px;
}
.hero-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.3), transparent);
    margin: 32px auto;
    max-width: 600px;
}

/* ── Section headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 24px 0 16px;
}
.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #e2e8f0;
}
.section-pill {
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.25);
    color: #38bdf8;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 100px;
}

/* ── Stat bar ── */
.stat-bar-wrap { margin: 6px 0; }
.stat-bar-label { color: #94a3b8; font-size: 13px; margin-bottom: 4px; display:flex; justify-content:space-between; }
.stat-bar-bg { background: rgba(255,255,255,0.05); border-radius: 100px; height: 8px; overflow:hidden; }
.stat-bar-fill-green { background: linear-gradient(90deg,#10b981,#059669); border-radius:100px; height:8px; transition:width 1s ease; }
.stat-bar-fill-red   { background: linear-gradient(90deg,#ef4444,#dc2626); border-radius:100px; height:8px; }
.stat-bar-fill-gray  { background: linear-gradient(90deg,#6b7280,#4b5563); border-radius:100px; height:8px; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(15,23,42,0.6) !important;
    border: 2px dashed rgba(56,189,248,0.25) !important;
    border-radius: 14px !important;
    padding: 20px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(56,189,248,0.5) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #38bdf8 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0f1e; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #38bdf8; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 8px;'>
        <div style='display:flex;align-items:center;gap:10px;'>
            <span style='font-size:26px;'>🔐</span>
            <div>
                <div style='font-size:15px;font-weight:700;color:#e2e8f0 !important;'>ForensicsAI</div>
                <div style='font-size:11px;color:#475569 !important;'>Manufacturing Security</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(56,189,248,0.15);margin:12px 0;'>", unsafe_allow_html=True)

    scan_mode = st.radio(
        "**Scan Mode**",
        ["📁 Scan Directory", "📤 Upload Files"],
        help="Choose input method for forensic analysis.",
    )

    st.markdown("<hr style='border-color:rgba(56,189,248,0.15);margin:12px 0;'>", unsafe_allow_html=True)

    hash_algo = st.selectbox(
        "**Hash Algorithm**",
        ["sha256", "md5"],
        help="SHA-256 is more secure; MD5 is faster.",
    )

    st.markdown("<hr style='border-color:rgba(56,189,248,0.15);margin:12px 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:12px;color:#475569 !important;text-transform:uppercase;letter-spacing:1px;font-weight:600;margin-bottom:10px;'>
        Forensic Rules
    </div>
    <div style='display:flex;flex-direction:column;gap:8px;'>
        <div style='background:rgba(14,165,233,0.08);border:1px solid rgba(14,165,233,0.2);border-radius:8px;padding:10px 12px;'>
            <div style='color:#38bdf8 !important;font-size:11px;font-weight:700;'>RULE 01</div>
            <div style='color:#94a3b8 !important;font-size:12px;margin-top:2px;'>Modified before creation</div>
        </div>
        <div style='background:rgba(14,165,233,0.08);border:1px solid rgba(14,165,233,0.2);border-radius:8px;padding:10px 12px;'>
            <div style='color:#38bdf8 !important;font-size:11px;font-weight:700;'>RULE 02</div>
            <div style='color:#94a3b8 !important;font-size:12px;margin-top:2px;'>Accessed before creation</div>
        </div>
        <div style='background:rgba(14,165,233,0.08);border:1px solid rgba(14,165,233,0.2);border-radius:8px;padding:10px 12px;'>
            <div style='color:#38bdf8 !important;font-size:11px;font-weight:700;'>RULE 03</div>
            <div style='color:#94a3b8 !important;font-size:12px;margin-top:2px;'>Modified after last access</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(56,189,248,0.15);margin:16px 0 8px;'>", unsafe_allow_html=True)
    st.markdown("<div style='color:#2d3748 !important;font-size:11px;text-align:center;'>v2.0 · Cloud Forensics Tool</div>", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
    <div class='hero-badge'>🏭 Manufacturing Breach Detection System</div>
    <div class='hero-title'>Cloud Forensics<br>Automation</div>
    <div class='hero-sub'>Detect file tampering · Extract metadata · Generate evidence reports</div>
    <div class='hero-divider'></div>
</div>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def render_metrics(metrics: dict):
    total = metrics["total_files"] or 1
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📂 Total Files",   metrics["total_files"])
    c2.metric("⚠️ Suspicious",    metrics["suspicious_files"])
    c3.metric("✅ Clean",          metrics["clean_files"])
    c4.metric("❓ Errors",         metrics["error_files"])
    c5.metric("🚨 Threat Rate",   f"{metrics['threat_rate']}%")

    # Visual stat bars
    susp_pct  = int(metrics["suspicious_files"] / total * 100)
    clean_pct = int(metrics["clean_files"] / total * 100)
    err_pct   = int(metrics["error_files"] / total * 100)

    st.markdown(f"""
    <div class='glass-card' style='margin-top:16px;'>
        <div style='font-size:13px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:16px;'>
            Distribution Overview &nbsp;·&nbsp; {metrics['total_size_kb']:,.2f} KB scanned
        </div>
        <div class='stat-bar-wrap'>
            <div class='stat-bar-label'><span>✅ Clean Files</span><span style='color:#10b981;'>{clean_pct}%</span></div>
            <div class='stat-bar-bg'><div class='stat-bar-fill-green' style='width:{clean_pct}%;'></div></div>
        </div>
        <div class='stat-bar-wrap' style='margin-top:12px;'>
            <div class='stat-bar-label'><span>⚠️ Suspicious Files</span><span style='color:#ef4444;'>{susp_pct}%</span></div>
            <div class='stat-bar-bg'><div class='stat-bar-fill-red' style='width:{susp_pct}%;'></div></div>
        </div>
        <div class='stat-bar-wrap' style='margin-top:12px;'>
            <div class='stat-bar-label'><span>❓ Error Files</span><span style='color:#6b7280;'>{err_pct}%</span></div>
            <div class='stat-bar-bg'><div class='stat-bar-fill-gray' style='width:{err_pct}%;'></div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_results(df: pd.DataFrame):
    st.markdown("""
    <div class='section-header'>
        <span style='font-size:20px;'>📊</span>
        <span class='section-title'>Scan Results</span>
        <span class='section-pill'>Full Evidence Report</span>
    </div>
    """, unsafe_allow_html=True)

    def hl(val):
        if val == "⚠️ YES":
            return "background-color:#450a0a;color:#fca5a5;font-weight:700;"
        elif val == "✅ Clean":
            return "background-color:#052e16;color:#6ee7b7;font-weight:600;"
        return "color:#64748b;"

    styled = df.style.map(hl, subset=["Suspicious"])
    st.dataframe(styled, use_container_width=True, height=400)

    col_dl, col_info = st.columns([1, 3])
    with col_dl:
        st.download_button(
            label="⬇️ Download CSV Report",
            data=to_csv_bytes(df),
            file_name="forensic_report.csv",
            mime="text/csv",
        )
    with col_info:
        st.markdown(
            f"<div style='color:#475569;font-size:13px;padding-top:12px;'>"
            f"📄 {len(df)} files · "
            f"🔐 Hash: <code style='color:#38bdf8;font-family:JetBrains Mono,monospace;'>"
            f"{df['Hash Algorithm'].iloc[0] if not df.empty else 'N/A'}</code></div>",
            unsafe_allow_html=True
        )


# ── Scan Mode: Directory ──────────────────────────────────────────────────────
if scan_mode == "📁 Scan Directory":
    st.markdown("""
    <div class='section-header'>
        <span style='font-size:22px;'>📁</span>
        <span class='section-title'>Directory Scanner</span>
        <span class='section-pill'>Recursive</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='info-box'>📌 Enter a full folder path. All files are scanned recursively for tampering indicators.</div>", unsafe_allow_html=True)

    dir_path = st.text_input(
        "Directory Path",
        value=os.path.join(os.getcwd(), "sample_data"),
        placeholder=r"e.g. C:\factory_logs\production",
    )

    if st.button("🔍 Launch Forensic Scan", key="scan_dir"):
        if not dir_path.strip():
            st.error("❌ Please enter a directory path.")
        else:
            with st.spinner("⏳ Scanning… extracting metadata & computing hashes…"):
                try:
                    df = scan_directory(dir_path.strip(), hash_algo=hash_algo)
                    if df.empty:
                        st.warning("⚠️ No files found in the specified directory.")
                    else:
                        metrics = compute_metrics(df)
                        st.markdown("""
                        <div class='section-header'>
                            <span style='font-size:22px;'>📈</span>
                            <span class='section-title'>Dashboard Metrics</span>
                        </div>
                        """, unsafe_allow_html=True)
                        render_metrics(metrics)

                        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

                        if metrics["suspicious_files"] > 0:
                            st.markdown(
                                f"<div class='warn-box'>🚨 <b>{metrics['suspicious_files']} suspicious file(s) detected!</b> "
                                f"Immediate review required. Threat rate: <b>{metrics['threat_rate']}%</b></div>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown("<div class='success-box'>✅ <b>All Clear!</b> No suspicious activity detected. All files passed forensic checks.</div>", unsafe_allow_html=True)

                        st.markdown("<hr style='border-color:rgba(56,189,248,0.1);margin:24px 0;'>", unsafe_allow_html=True)
                        render_results(df)

                except ValueError as e:
                    st.error(f"❌ Invalid path: {e}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {e}")


# ── Scan Mode: Upload ─────────────────────────────────────────────────────────
elif scan_mode == "📤 Upload Files":
    st.markdown("""
    <div class='section-header'>
        <span style='font-size:22px;'>📤</span>
        <span class='section-title'>File Upload Scanner</span>
        <span class='section-pill'>Multi-file</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='info-box'>📎 Upload one or more files. Metadata is extracted and each file is checked for forensic anomalies.</div>", unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop files here or click to browse",
        accept_multiple_files=True,
        help="Supports all file types. Multiple files allowed.",
    )

    if uploaded:
        st.markdown(
            f"<div class='success-box'>📁 <b>{len(uploaded)} file(s)</b> ready for analysis.</div>",
            unsafe_allow_html=True
        )
        if st.button("🔍 Launch Forensic Scan", key="scan_upload"):
            with st.spinner("⏳ Analysing uploaded files…"):
                try:
                    df = scan_uploaded_files(uploaded, hash_algo=hash_algo)
                    if df.empty:
                        st.warning("⚠️ No metadata could be extracted.")
                    else:
                        metrics = compute_metrics(df)
                        st.markdown("""
                        <div class='section-header'>
                            <span style='font-size:22px;'>📈</span>
                            <span class='section-title'>Dashboard Metrics</span>
                        </div>
                        """, unsafe_allow_html=True)
                        render_metrics(metrics)

                        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

                        if metrics["suspicious_files"] > 0:
                            st.markdown(
                                f"<div class='warn-box'>🚨 <b>{metrics['suspicious_files']} suspicious file(s) detected!</b> "
                                f"Threat rate: <b>{metrics['threat_rate']}%</b> — Review highlighted rows.</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown("<div class='success-box'>✅ <b>All Clear!</b> No anomalies detected across all uploaded files.</div>", unsafe_allow_html=True)

                        st.markdown("<hr style='border-color:rgba(56,189,248,0.1);margin:24px 0;'>", unsafe_allow_html=True)
                        render_results(df)

                except Exception as e:
                    st.error(f"❌ Error during scan: {e}")
    else:
        st.markdown("""
        <div style='text-align:center;padding:40px 20px;color:#1e3a5f;'>
            <div style='font-size:48px;margin-bottom:12px;'>📂</div>
            <div style='font-size:16px;font-weight:600;color:#334155;'>Upload files to begin forensic analysis</div>
            <div style='font-size:13px;color:#1e293b;margin-top:6px;'>Supports all file types · No size limit</div>
        </div>
        """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style='border-color:rgba(56,189,248,0.08);margin-top:48px;'>
<div style='text-align:center;padding:16px 0 8px;'>
    <div style='color:#1e293b;font-size:12px;letter-spacing:0.5px;'>
        🔐 <b style='color:#334155;'>Cloud Forensics Automation</b> &nbsp;·&nbsp;
        Manufacturing Breach Detection &nbsp;·&nbsp;
        Built with Python + Streamlit
    </div>
</div>
""", unsafe_allow_html=True)
