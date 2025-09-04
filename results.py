import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import os

# 🔹 Helper to build a download link (for local resumes only)
def make_download_link(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        fname = os.path.basename(file_path)
        return f'<a href="data:application/octet-stream;base64,{b64}" download="{fname}">📂 Download</a>'
    except Exception:
        return None  # No link if not valid

def render_results(results):
    df = pd.DataFrame(results).sort_values(by="Score (%)", ascending=False).reset_index(drop=True)
    df.index += 1

    # ✅ Only add "Download Resume" column if file paths look real
    if "File Path" in df.columns and df["File Path"].notnull().any():
        df["Download Resume"] = [make_download_link(p) if os.path.exists(str(p)) else None for p in df["File Path"]]
        df.drop(columns=["File Path"], inplace=True)

    st.subheader("📊 Candidate Screening Results")

    # If "Download Resume" exists, render with HTML to keep links clickable
    if "Download Resume" in df.columns:
        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.dataframe(df)

    # ✅ Global download button (safe in all cases)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Candidate Screening Results",
        data=csv,
        file_name="candidate_screening_results.csv",
        mime="text/csv"
    )

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1: 
        st.metric("Total Resumes", len(df))
    with col2: 
        st.metric("Qualified", (df["Qualified"] == "✅ Yes").sum())
    with col3: 
        st.metric("Unqualified", (df["Qualified"] == "❌ No").sum())

    # Score Distribution
    fig, ax = plt.subplots()
    df["Score (%)"].astype(float).plot(kind="hist", bins=10, ax=ax, color="skyblue", edgecolor="black")
    ax.set_xlabel("Match Score (%)")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)
