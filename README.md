# Smart CV Shortlisting (AI Resume Screening)

📄 **Smart CV Shortlisting** is a Streamlit-based web app that helps recruiters and hiring managers 
automatically screen, rank, and shortlist resumes based on job descriptions.

## 🚀 Features
- Upload multiple resumes (PDF/DOCX)
- Paste any job description
- AI-powered **semantic similarity** scoring (using Sentence Transformers)
- Automatic **experience extraction** from job history
- **Fuzzy skill matching** (handles variations like "ML" vs "Machine Learning")
- Candidate **qualification filtering** (score, experience, location, skills)
- Export results as **CSV**
- Download resumes directly from the results

## 📂 Input Modes
1. **Upload Mode (Public)** → upload resumes directly in the app.
2. **Folder Mode (Local)** → scan resumes from `resumes_to_process/` folder (useful if running locally).

## 🛠️ Tech Stack
- Python 3.9+
- Streamlit
- Pandas
- scikit-learn
- PyPDF2
- python-docx
- rapidfuzz
- sentence-transformers

## 💻 How to Run Locally
```bash
pip install -r requirements.txt
streamlit run Smart_Resume_Shortlisting_System.py
