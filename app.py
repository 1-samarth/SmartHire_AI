import os
import re
import streamlit as st
import pandas as pd

from resume_parser import extract_text
from scoring_system import calculate_score
from email_sender import send_email
from skill_extractor import extract_skills
from ranking_system import rank_candidates
from email_reader import fetch_resumes

st.set_page_config(page_title="SmartHire AI", layout="wide")

with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Session state setup
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "shortlisted_candidates" not in st.session_state:
    st.session_state.shortlisted_candidates = []
if "rejected_candidates" not in st.session_state:
    st.session_state.rejected_candidates = []
if "emailed_candidates" not in st.session_state:
    st.session_state.emailed_candidates = []
if "manual_candidates" not in st.session_state:
    st.session_state.manual_candidates = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

st.title("🤖 SmartHire AI – Recruitment Dashboard")

# Sidebar HR Controls
st.sidebar.header("HR Job Requirements")
job_role = st.sidebar.text_input("Job Role")
skills_input = st.sidebar.text_input("Required Skills (comma separated)")
skills = [s.strip().lower() for s in skills_input.split(",") if s]

# 🔥 Stylish Skills Display
st.sidebar.markdown("### 🎯 Skills Selected")
skill_colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728", "#9467bd", "#8c564b"]

if skills:
    skill_tags = ""
    for i, skill in enumerate(skills):
        color = skill_colors[i % len(skill_colors)]
        skill_tags += f"<span style='background-color:{color}; color:white; padding:6px 12px; border-radius:15px; margin:4px; display:inline-block; font-size:14px;'>{skill}</span>"
    st.sidebar.markdown(skill_tags, unsafe_allow_html=True)
else:
    st.sidebar.info("No skills selected yet.")

st.divider()

# Helper functions
def extract_candidate_name(text):
    lines = text.splitlines()
    for line in lines:
        if "name" in line.lower():
            return line.split(":")[-1].strip()
    for line in lines:
        if line.strip():
            return line.strip()
    return "Unknown Candidate"

def add_candidate_once(candidate_name, score, email=None, phone=None):
    if not candidate_name:
        return
    already_exists = any(c["Candidate"] == candidate_name for c in st.session_state.candidates)
    if not already_exists:
        st.session_state.candidates.append({
            "Candidate": candidate_name,
            "Score": score,
            "Email": email,
            "Phone": phone
        })

def shortlist_candidate(candidate_name):
    if candidate_name not in st.session_state.shortlisted_candidates:
        st.session_state.shortlisted_candidates.append(candidate_name)
    if candidate_name in st.session_state.rejected_candidates:
        st.session_state.rejected_candidates.remove(candidate_name)

def reject_candidate(candidate_name):
    if candidate_name not in st.session_state.rejected_candidates:
        st.session_state.rejected_candidates.append(candidate_name)
    if candidate_name in st.session_state.shortlisted_candidates:
        st.session_state.shortlisted_candidates.remove(candidate_name)

# 📥 Email Applications Section
st.header("📥 Email Applications")
if st.button("Check Email Applications"):
    resumes, error = fetch_resumes()
    if error:
        st.error(f"Email reader error: {error}")
    else:
        if not resumes:
            st.info("No new resume attachments found in email.")
        else:
            processed = 0
            for r in resumes:
                try:
                    text = extract_text(r)
                    detected_skills = extract_skills(text)
                    score, matched = calculate_score(text, skills)
                    candidate_name = extract_candidate_name(text)

                    emails_found = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
                    candidate_email = emails_found[0] if emails_found else None
                    phones_found = re.findall(r"\+?\d[\d\s-]{8,}", text)
                    candidate_phone = phones_found[0] if phones_found else None

                    add_candidate_once(candidate_name, score, candidate_email, candidate_phone)

                    if score >= 40:
                        shortlist_candidate(candidate_name)
                        if candidate_email and candidate_email not in st.session_state.emailed_candidates:
                            ok, msg = send_email(candidate_email)
                            if ok:
                                st.session_state.emailed_candidates.append(candidate_email)
                                st.success(f"📧 Interview Email Sent Automatically to {candidate_name}")
                            else:
                                st.error(f"Email error for {candidate_name}: {msg}")
                    else:
                        reject_candidate(candidate_name)
                    processed += 1
                except Exception as e:
                    st.warning(f"Could not process {r}: {e}")
            st.success(f"📩 Email resumes processed successfully: {processed}")

# 📊 HR Candidate Dashboard
st.divider()
st.header("📊 HR Candidate Dashboard")

st.subheader("✅ Shortlisted Candidates")
shortlisted_data = [c for c in st.session_state.candidates if c["Candidate"] in st.session_state.shortlisted_candidates]
if shortlisted_data:
    ranked_shortlisted = rank_candidates(shortlisted_data)
    ranked_shortlisted.insert(0, "ArrivalOrder", range(1, len(ranked_shortlisted) + 1))
    st.dataframe(ranked_shortlisted, use_container_width=True, hide_index=True)
else:
    st.write("No shortlisted candidates yet.")

st.subheader("❌ Rejected Candidates")
rejected_data = [c for c in st.session_state.candidates if c["Candidate"] in st.session_state.rejected_candidates]
if rejected_data:
    ranked_rejected = rank_candidates(rejected_data)
    ranked_rejected.insert(0, "ArrivalOrder", range(1, len(ranked_rejected) + 1))
    st.dataframe(ranked_rejected, use_container_width=True, hide_index=True)
else:
    st.write("No rejected candidates yet.")

# 📤 Manual Resume Evaluation
st.divider()
st.header("📤 Manual Resume Evaluation for Custom Interview Invite Candidates")

uploaded_file = st.file_uploader(
    "Upload Resume (PDF/DOCX)", 
    type=["pdf","docx"], 
    key=f"uploader_{st.session_state.uploader_key}"
)

if uploaded_file is not None:
    try:
        text = extract_text(uploaded_file)
        score, matched = calculate_score(text, skills)
        candidate_name = extract_candidate_name(text)

        emails_found = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        candidate_email = emails_found[0] if emails_found else None
        phones_found = re.findall(r"\+?\d[\d\s-]{8,}", text)
        candidate_phone = phones_found[0] if phones_found else None

        manual_candidate = {
            "Candidate": candidate_name,
            "Score": score,
            "Email": candidate_email,
            "Phone": candidate_phone
        }

        already_exists = any(
            c["Candidate"] == candidate_name and c["Email"] == candidate_email
            for c in st.session_state.manual_candidates
        )
        if not already_exists:
            st.session_state.manual_candidates.append(manual_candidate)

        # Reset uploader key so file name disappears
        st.session_state.uploader_key += 1

    except Exception as e:
        st.error(f"Error processing resume: {e}")

if st.session_state.manual_candidates:
    df_manual = pd.DataFrame(st.session_state.manual_candidates)
    df_manual = rank_candidates(df_manual.to_dict("records"))
    df_manual.insert(0, "ArrivalOrder", range(1, len(df_manual) + 1))
    st.dataframe(df_manual, use_container_width=True, hide_index=True)

# 📩 Custom Interview Invite Section
st.divider()
st.header("📩 Custom Interview Invite")

manual_email = st.text_input("Enter Candidate Email for Custom Invite")
if st.button("Send Custom Interview Invite"):
    if manual_email:
        ok, msg = send_email(manual_email)
        if ok:
            st.success("📧 Custom Interview Email Sent Successfully")
        else:
            st.error(f"Email error: {msg}")
