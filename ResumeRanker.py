import streamlit as st
import pandas as pd
import PyPDF2
import docx
import os
import re
import base64
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Resume Ranker", layout="wide")

# ----------------- CUSTOM STYLING -----------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 50px;
        font-weight: bold;
        text-align: center;
        color: #2E86C1;
        padding: 20px 0;
    }
    .subtitle {
        font-size: 22px;
        text-align: center;
        color: #555;
        margin-bottom: 30px;
    }
    .info-box {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .success {background-color: #e8f5e9; color: #2e7d32;}
    .warning {background-color: #fff3e0; color: #ef6c00;}
    .error {background-color: #ffebee; color: #c62828;}
    </style>
    <div class="main-title">📂 Resume Ranker</div>
    <div class="subtitle">Smart Resume Shortlisting System</div>
    """,
    unsafe_allow_html=True
)

# ----------------- MODEL LOADING (cached) -----------------
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# ----------------- HELPER FUNCTIONS -----------------
@st.cache_data
def extract_text_from_path(file_path):
    """Extract text from a PDF or DOCX file path."""
    try:
        text = ""
        if file_path.endswith(".pdf"):
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    if page.extract_text():
                        text += page.extract_text() + "\n"
        elif file_path.endswith(".docx"):
            with open(file_path, "rb") as f:
                document = docx.Document(f)
                for para in document.paragraphs:
                    text += para.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error processing {os.path.basename(file_path)}: {str(e)}")
        return ""


def extract_experience(text):
    """Extract total years of experience from job date ranges."""
    clean_text = text.replace("’", "'").replace("–", "-").replace("—", "-")
    date_patterns = re.findall(
        r"([A-Za-z]{3,9})[\' ]?(\d{2,4})\s*[-to]+\s*([A-Za-z]{3,9})[\' ]?(\d{2,4}|date|present)",
        clean_text,
        re.IGNORECASE,
    )

    total_months = 0
    for start_month, start_year, end_month, end_year in date_patterns:
        try:
            start_year = int("20" + start_year if len(start_year) == 2 else start_year)
            end_year = (
                datetime.now().year
                if end_year.lower() in ["date", "present"]
                else int("20" + end_year if len(end_year) == 2 else end_year)
            )

            start_date = datetime.strptime(f"{start_month} {start_year}", "%b %Y")
            try:
                end_date = datetime.strptime(f"{end_month} {end_year}", "%b %Y")
            except ValueError:
                end_date = datetime.strptime(f"{end_month} {end_year}", "%B %Y")

            months = (end_date.year - start_date.year) * 12 + (
                end_date.month - start_date.month
            )
            if months > 0:
                total_months += months
        except Exception:
            continue

    return round(total_months / 12, 1)  # in years


def calculate_similarity(jd_text, resume_text):
    """Semantic similarity between JD and resume text."""
    if not jd_text.strip() or not resume_text.strip():
        return 0
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    similarity = util.cos_sim(jd_embedding, resume_embedding).item()
    return round(similarity * 100, 2)


def match_skills(required_skills, resume_text, threshold=80):
    """Match required skills with fuzzy matching."""
    matched = []
    resume_text_lower = resume_text.lower()

    for skill in required_skills:
        skill_lower = skill.lower()
        if re.search(r"\b" + re.escape(skill_lower) + r"\b", resume_text_lower):
            matched.append(skill)
        else:
            if fuzz.partial_ratio(skill_lower, resume_text_lower) >= threshold:
                matched.append(skill)

    return list(set(matched))

# ----------------- APP UI -----------------
jd_text = st.text_area("📑 Paste Job Description", height=200)

col1, col2 = st.columns(2)
with col1:
    min_score = st.slider("Minimum Match Score (%)", 0, 100, 50)
    min_exp = st.slider("Minimum Experience (years)", 0, 20, 2)
with col2:
    skills_filter = st.text_input(
        "Required skills (comma-separated)", "Python, SQL, Machine Learning"
    )
    location_filter = st.text_input("Preferred Location (optional)")

mode = st.radio("Choose Input Mode:", ["📂 Folder Mode (Local)", "☁️ Upload Mode (Public)"])

results = []
resume_files_paths = []

if mode == "📂 Folder Mode (Local)":
    resume_folder = "resumes_to_process"
    if not os.path.exists(resume_folder):
        os.makedirs(resume_folder)
        st.warning(f"Created a folder named '{resume_folder}'. Please add your resumes there.")

    if st.button("Process Resumes (Folder)", type="primary", use_container_width=True):
        resume_files_paths = [
            os.path.join(resume_folder, f)
            for f in os.listdir(resume_folder)
            if f.endswith((".pdf", ".docx"))
        ]

elif mode == "☁️ Upload Mode (Public)":
    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True
    )
    if uploaded_files and st.button("Process Resumes (Uploads)", type="primary", use_container_width=True):
        temp_folder = "temp_uploads"
        os.makedirs(temp_folder, exist_ok=True)
        for uploaded_file in uploaded_files:
            resume_path = os.path.join(temp_folder, uploaded_file.name)
            with open(resume_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            resume_files_paths.append(resume_path)

# ----------------- PROCESSING -----------------
if resume_files_paths:
    if not jd_text.strip():
        st.warning("⚠️ Please provide a Job Description.")
    else:
        with st.spinner("Processing resumes..."):
            required_skills = [s.strip().lower() for s in skills_filter.split(",") if s.strip()]

            for file_path in resume_files_paths:
                file_name = os.path.basename(file_path)

                text = extract_text_from_path(file_path)
                if not text:
                    continue

                score = calculate_similarity(jd_text, text)
                experience = extract_experience(text)
                matched_skills = match_skills(required_skills, text)
                location_match = not location_filter.strip() or (location_filter.strip().lower() in text.lower())

                is_qualified = (
                    score >= min_score
                    and experience >= min_exp
                    and location_match
                    and (len(matched_skills) > 0 if required_skills else True)
                )

                results.append(
                    {
                        "Resume": file_name,
                        "Score (%)": round(score, 2),
                        "Experience (yrs)": round(experience, 1),
                        "Qualified": "✅ Yes" if is_qualified else "❌ No",
                        "Matched Skills": ", ".join(list(set(matched_skills))) or "None",
                        "Location Match": "✅ Yes" if location_match else "❌ No",
                        "File Path": file_path
                    }
                )

        if results:
            df = pd.DataFrame(results).sort_values(by="Score (%)", ascending=False).reset_index(drop=True)
            df.index += 1

            df["Score (%)"] = df["Score (%)"].map(lambda x: f"{x:.2f}")
            df["Experience (yrs)"] = df["Experience (yrs)"].map(lambda x: f"{x:.1f}")


            # Add clickable links for each resume
            def make_download_link(file_path):
                """
                Returns an HTML download link for a resume file.
                Works on Streamlit Cloud.
                """
                try:
                    with open(file_path, "rb") as f:
                        data = f.read()
                    b64 = base64.b64encode(data).decode()  # encode file to base64
                    file_name = os.path.basename(file_path)
                    return f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">📂 Download</a>'
                except Exception as e:
                    return f"❌ Error: {str(e)}"
                    
            df["Download Resume"] = [make_download_link(path) for path in df["File Path"]]

            # Function to render styled table
            def render_table(dataframe, title):
                st.subheader(title)
                if dataframe.empty:
                    st.info("No data available.")
                else:
                    styled_df = (
                        dataframe.style
                        .set_table_styles(
                            [{"selector": "th", "props": [("text-align", "left")]}]  # align headers left
                        )
                        .set_properties(**{"text-align": "left"})  # align cell text left
                    )
                    st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)

            # ✅ Qualified Candidates
            render_table(df[df["Qualified"] == "✅ Yes"], "✅ Qualified Candidates")

            # ❌ Unqualified Candidates
            render_table(df[df["Qualified"] == "❌ No"], "❌ Unqualified Candidates")

            # 📥 Export All Results as CSV
            csv = df.to_csv(index_label="Rank").encode("utf-8")
            st.download_button("📥 Download Full Results (CSV)", csv, "resume_ranking.csv", "text/csv")

# ----------------- FOOTER -----------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 15px; font-size: 18px; font-family: cursive; color: grey;">
        ✍️ Developed by <b>Md Sarfraaz</b>
    </div>
    """,
    unsafe_allow_html=True
)
