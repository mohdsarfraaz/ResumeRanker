import streamlit as st
import PyPDF2
import docx

def job_description_section():
    st.subheader("📑 Job Description")
    jd_text = ""

    col1, col2 = st.columns([2, 1])
    with col2:
        jd_mode = st.radio("Choose input method:", ["✍️ Paste JD", "📂 Upload JD File"])

    with col1:
        if jd_mode == "✍️ Paste JD":
            jd_text = st.text_area("Paste Job Description Here", height=200)
        elif jd_mode == "📂 Upload JD File":
            uploaded_jd = st.file_uploader("Upload JD (TXT, DOCX, PDF)", type=["txt", "docx", "pdf"])
            if uploaded_jd:
                if uploaded_jd.name.endswith(".txt"):
                    jd_text = uploaded_jd.read().decode("utf-8")
                elif uploaded_jd.name.endswith(".docx"):
                    doc = docx.Document(uploaded_jd)
                    jd_text = "\n".join([p.text for p in doc.paragraphs])
                elif uploaded_jd.name.endswith(".pdf"):
                    pdf_reader = PyPDF2.PdfReader(uploaded_jd)
                    jd_text = "\n".join([p.extract_text() for p in pdf_reader.pages if p.extract_text()])
                st.success("✅ Job Description loaded successfully!")
                st.text_area("Preview JD", jd_text[:1500], height=200)

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        min_score = st.slider("Minimum Match Score (%)", 0, 100, 50)
        min_exp = st.slider("Minimum Experience (years)", 0, 20, 2)
    with col2:
        skills_filter = st.text_input("Required skills (comma-separated)", "Python, SQL, Machine Learning")
        location_filter = st.text_input("Preferred Location (optional)")

    mode = st.radio("Choose Input Mode:", ["📂 Folder Mode (Local)", "☁️ Upload Mode (Public)"])

    filters = {
        "min_score": min_score,
        "min_exp": min_exp,
        "skills_filter": skills_filter,
        "location_filter": location_filter,
        "mode": mode
    }

    return jd_text, filters
