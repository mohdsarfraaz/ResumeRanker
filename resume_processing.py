import streamlit as st
import os
import base64
import pandas as pd
from utils import extract_text_from_path, extract_experience, calculate_similarity, match_skills

def process_resumes(jd_text, filters):
    results = []
    resume_files = []

    if filters["mode"] == "📂 Folder Mode (Local)":
        resume_folder = "resumes_to_process"
        os.makedirs(resume_folder, exist_ok=True)
        if st.button("⚡ Process Resumes (Folder)", type="primary", use_container_width=True):
            resume_files = [os.path.join(resume_folder, f) for f in os.listdir(resume_folder) if f.endswith((".pdf",".docx"))]

    elif filters["mode"] == "☁️ Upload Mode (Public)":
        uploaded_files = st.file_uploader("📤 Upload Resumes", type=["pdf","docx"], accept_multiple_files=True)
        if uploaded_files and st.button("⚡ Process Resumes (Uploads)", type="primary", use_container_width=True):
            upload_folder = "uploaded_resumes"
            os.makedirs(upload_folder, exist_ok=True)
            for f in uploaded_files:
                path = os.path.join(upload_folder, f.name)
                with open(path,"wb") as out: out.write(f.getbuffer())
                resume_files.append(path)
            st.success(f"✅ {len(resume_files)} resumes saved in '{upload_folder}' folder")

    if resume_files and jd_text.strip():
        required_skills = [s.strip().lower() for s in filters["skills_filter"].split(",") if s.strip()]
        for path in resume_files:
            text = extract_text_from_path(path)
            if not text: continue
            score = calculate_similarity(jd_text, text)
            exp = extract_experience(text)
            skills = match_skills(required_skills, text)
            loc_match = not filters["location_filter"].strip() or filters["location_filter"].lower() in text.lower()
            qualified = score >= filters["min_score"] and exp >= filters["min_exp"] and loc_match and (len(skills)>0 if required_skills else True)

            results.append({
                "Resume": os.path.basename(path),
                "Score (%)": round(score,2),
                "Experience (yrs)": round(exp,1),
                "Qualified": "✅ Yes" if qualified else "❌ No",
                "Matched Skills": ", ".join(set(skills)) or "None",
                "Location Match": "✅ Yes" if loc_match else "❌ No",
                "File Path": path
            })
    return resume_files, results
