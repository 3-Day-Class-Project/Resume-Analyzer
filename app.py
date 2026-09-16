import streamlit as st

from resume_parser import extract_resume_text
from analyzer import analyze_resume

st.set_page_config(page_title="AI Resume Analyzer")
st.title("AI Resume Analyzer")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
job_description = st.text_area("Paste the job description")

resume_text = ""
if uploaded_file is not None:
    try:
        resume_text = extract_resume_text(uploaded_file)
        st.subheader("Extracted resume text")
        if resume_text:
            st.text_area("Resume text", resume_text, height=400, label_visibility="collapsed")
        else:
            st.warning("The PDF was opened, but no selectable text was found. It may be scanned or image-only.")
    except Exception as exc:
        st.error(f"Could not extract text from the uploaded PDF: {exc}")

if st.button("Analyze Resume"):
    if uploaded_file is None:
        st.error("Please upload a PDF resume.")
    elif not job_description.strip():
        st.error("Please paste a job description.")
    elif not resume_text:
        st.error("No resume text could be extracted from this PDF.")
    else:
        try:
            result = analyze_resume(resume_text, job_description)
            st.metric("Match Score", f"{result['match_score']}%")
            st.subheader("Matching Skills")
            for skill in result['matching_skills']:
                st.write(f"✓ {skill}")
            st.subheader("Requested Skills Not Identified")
            for skill in result['missing_skills']:
                st.write(f"⚠ {skill}")
            st.subheader("Suggestions")
            for suggestion in result['suggestions']:
                st.write(f"• {suggestion}")
        except NotImplementedError:
            st.info("The integration shell is ready; parser/analyzer modules still need implementation.")
        except Exception as exc:
            st.error(f"Analysis could not be completed: {exc}")
