import hashlib
import streamlit as st
import os
import pandas as pd
from datetime import datetime, timedelta
import tempfile

st.title("🔍 Cloud Forensics Automation System")

# ------------------ Hash Function ------------------
def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

# ------------------ Option Selection ------------------
option = st.radio("Choose Input Method:", ["Enter Folder Path", "Upload Files"])

files = []

# ------------------ OPTION 1: Folder Path ------------------
if option == "Enter Folder Path":
    folder_path = st.text_input("Enter Folder Path")

    if st.button("Scan Folder"):
        if os.path.exists(folder_path):
            for root, dirs, filenames in os.walk(folder_path):
                for file in filenames:
                    files.append(os.path.join(root, file))
        else:
            st.error("❌ Invalid folder path")

# ------------------ OPTION 2: File Upload ------------------
elif option == "Upload Files":
    uploaded_files = st.file_uploader("Upload Files", accept_multiple_files=True)

    if uploaded_files:
        temp_dir = tempfile.mkdtemp()

        for uploaded_file in uploaded_files:
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())
            files.append(temp_path)

# ------------------ PROCESS FILES ------------------
if files:
    file_data = []

    for file in files:
        stats = os.stat(file)

        created_time = datetime.fromtimestamp(stats.st_ctime)
        modified_time = datetime.fromtimestamp(stats.st_mtime)
        accessed_time = datetime.fromtimestamp(stats.st_atime)
        file_size = stats.st_size

        file_hash = get_file_hash(file)

        file_data.append([
            os.path.basename(file),
            file,
            created_time,
            modified_time,
            accessed_time,
            file_size,
            file_hash
        ])

    # ------------------ Create DataFrame ------------------
    df = pd.DataFrame(file_data, columns=[
        "File Name",
        "File Path",
        "Created Time",
        "Modified Time",
        "Accessed Time",
        "File Size",
        "MD5 Hash"
    ])

    # ------------------ Suspicious Detection ------------------
    current_time = datetime.now()
    threshold = current_time - timedelta(hours=1)

    df["Suspicious"] = df.apply(
        lambda row: "YES" if (row["Modified Time"] > threshold and row["Created Time"] < row["Modified Time"]) else "NO",
        axis=1
    )

    st.success("✅ Scan Completed")

    # ------------------ Highlight Function ------------------
    def highlight_suspicious(row):
        if row["Suspicious"] == "YES":
            return ["background-color: red"] * len(row)
        else:
            return [""] * len(row)

    # ------------------ Show Full Table ------------------
    st.subheader("📁 All Files")
    st.dataframe(df.style.apply(highlight_suspicious, axis=1))

    # ------------------ Chart ------------------
    st.subheader("📊 Suspicious vs Normal Files")
    count_data = df["Suspicious"].value_counts()
    st.bar_chart(count_data)

    # ------------------ Suspicious Only ------------------
    st.subheader("🔴 Suspicious Files Only")
    st.dataframe(df[df["Suspicious"] == "YES"])

    # ------------------ Download Report ------------------
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Report", csv, "forensic_report.csv", "text/csv")