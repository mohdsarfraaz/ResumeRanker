import re
import os
import PyPDF2
import docx
from datetime import datetime
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util

# Load once
model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_path(file_path):
    text = ""
    try:
        if file_path.endswith(".pdf"):
            with open(file_path,"rb") as f:
                reader = PyPDF2.PdfReader(f)
                for p in reader.pages: 
                    if p.extract_text(): text += p.extract_text()+"\n"
        elif file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text+"\n"
    except Exception as e:
        return ""
    return text.strip()

def extract_experience(text):
    clean = text.replace("’","'").replace("–","-").replace("—","-")
    dates = re.findall(r"([A-Za-z]{3,9})[\' ]?(\d{2,4})\s*[-to]+\s*([A-Za-z]{3,9})[\' ]?(\d{2,4}|date|present)", clean, re.I)
    total = 0
    for sm,sy,em,ey in dates:
        try:
            sy = int("20"+sy if len(sy)==2 else sy)
            ey = datetime.now().year if ey.lower() in ["date","present"] else int("20"+ey if len(ey)==2 else ey)
            sdate = datetime.strptime(f"{sm} {sy}","%b %Y")
            try: edate = datetime.strptime(f"{em} {ey}","%b %Y")
            except: edate = datetime.strptime(f"{em} {ey}","%B %Y")
            months = (edate.year-sdate.year)*12 + (edate.month-sdate.month)
            if months>0: total += months
        except: continue
    return round(total/12,1)

def calculate_similarity(jd_text,resume_text):
    if not jd_text.strip() or not resume_text.strip(): return 0
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    res_emb = model.encode(resume_text, convert_to_tensor=True)
    return round(util.cos_sim(jd_emb, res_emb).item()*100,2)

def match_skills(required_skills,resume_text,threshold=80):
    matched = []
    res_low = resume_text.lower()
    for skill in required_skills:
        sk = skill.lower()
        if re.search(r"\b"+re.escape(sk)+r"\b", res_low): matched.append(skill)
        elif fuzz.partial_ratio(sk, res_low) >= threshold: matched.append(skill)
    return list(set(matched))
