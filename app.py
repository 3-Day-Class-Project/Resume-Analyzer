import streamlit as st

from analyzer import analyze_resume
from database import get_recent_analyses, save_analysis, clear_analyses
from resume_parser import extract_resume_text


st.set_page_config(page_title="AI Resume Analyzer")
st.title("AI Resume Analyzer")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
job_title = st.text_input("Job title (optional)")
job_description = st.text_area("Paste the job description")

resume_text = ""
if uploaded_file is not None:
    try:
        resume_text = extract_resume_text(uploaded_file)
        st.subheader("Extracted resume text")
        if resume_text:
            st.text_area(
                "Resume text",
                resume_text,
                height=400,
                label_visibility="collapsed",
            )
        else:
            st.warning(
                "The PDF was opened, but no selectable text was found. "
                "It may be scanned or image-only."
            )
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

            save_analysis(
                resume_name=uploaded_file.name,
                job_title=job_title,
                match_score=result["match_score"],
            )

            st.metric("Match Score", f"{result['match_score']}%")

            st.subheader("Exact Skill Matches")
            if result["matching_skills"]:
                for skill in result["matching_skills"]:
                    st.write(f"✓ {skill}")
            else:
                st.write("No exact requested skills were identified.")

            st.subheader("Related Experience")
            if result.get("related_skills"):
                for item in result["related_skills"]:
                    evidence = ", ".join(item["evidence"])
                    st.write(f"~ {item['skill']} — related evidence: {evidence}")
            else:
                st.write("No related evidence identified.")

            st.subheader("Requested Skills Not Identified")
            if result["missing_skills"]:
                for skill in result["missing_skills"]:
                    st.write(f"⚠ {skill}")
            else:
                st.write("No requested skills are completely missing.")

            st.subheader("Suggestions")
            for suggestion in result["suggestions"]:
                st.write(f"• {suggestion}")

            st.success("Analysis saved to history.")

        except Exception as exc:
            st.error(f"Analysis could not be completed: {exc}")

st.divider()
st.subheader("Recent Analyses")

try:
    recent_analyses = get_recent_analyses(limit=5)

    if recent_analyses:
        history_rows = [
            {
                "Resume": row["resume_name"],
                "Job Title": row["job_title"] or "Not provided",
                "Match Score": f"{row['match_score']}%",
                "Analyzed": row["created_at"],
            }
            for row in recent_analyses
        ]

        st.dataframe(
            history_rows,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("No saved analyses yet.")
    
    
    delete_analyses = clear_analyses()
    st.button("Clear", on_click=clear_analyses(), type="primary")

except Exception as exc:
    st.warning(f"Could not load analysis history: {exc}")
    

