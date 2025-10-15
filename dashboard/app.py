import streamlit as st
import requests
import json
import pandas as pd

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Smart Resume Screener", layout="wide")
st.title("Smart Resume Screener")

tab1, tab2, tab3, tab4 = st.tabs([
    "Upload Resumes",
    "Create Job",
    "Shortlist (Semantic)",
    "Explain Candidate"
])

with tab1:
    st.subheader("Upload a Resume")
    f = st.file_uploader("Choose a resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
    if f and st.button("Upload"):
        files = {"file": (f.name, f.getvalue())}
        try:
            r = requests.post(f"{API}/resumes/upload", files=files, timeout=120)
            if r.ok:
                data = r.json()
                st.success(f"Uploaded successfully! Resume ID: {data['resume_id']}")
                st.json(data)
            else:
                st.error(f"Upload failed: {r.text}")
        except Exception as e:
            st.error(f"Request error: {e}")

with tab2:
    st.subheader("Create a Job Description")
    title = st.text_input("Job Title", "Machine Learning Engineer")
    jd_text = st.text_area(
        "Job Description",
        "We need experience with Python, AWS, Transformers, and MLOps. Minimum 3 years in production ML."
    )
    must_have_str = st.text_input("Must-have skills (comma-separated)", "Python, AWS, Transformers")
    min_years = st.number_input("Minimum years of experience", 0, 40, 3)

    if st.button("Create Job"):
        payload = {
            "title": title,
            "jd_text": jd_text,
            "must_have": [s.strip() for s in must_have_str.split(",") if s.strip()],
            "min_years": int(min_years),
        }
        try:
            r = requests.post(f"{API}/jobs/create", json=payload)
            if r.ok:
                job = r.json()
                st.success(f"Job created! Job ID: {job['id']}")
                st.json(job)
            else:
                st.error(r.text)
        except Exception as e:
            st.error(f"Request error: {e}")

with tab3:
    st.subheader("Get Semantic Shortlist")

    job_id = st.number_input("Job ID", 1, step=1)
    k = st.slider("Top K Candidates", 1, 20, 5)
    w_sem = st.slider("Weight: Semantic", 0.0, 1.0, 0.45, 0.05)
    w_skill = st.slider("Weight: Skills", 0.0, 1.0, 0.30, 0.05)
    w_exp = st.slider("Weight: Experience", 0.0, 1.0, 0.20, 0.05)

    if st.button("Shortlist"):
        params = {"job_id": int(job_id), "k": int(k)}
        try:
            r = requests.get(f"{API}/match/shortlist_semantic", params=params, timeout=120)
            if r.ok:
                rows = r.json()
                if not rows:
                    st.warning("No candidates found. Try uploading resumes first.")
                else:
                    st.write(f"### Top {len(rows)} Candidates")
                    df_rows = []
                    for c in rows:
                        df_rows.append({
                            "Candidate ID": c["candidate_id"],
                            "Score": c["score"],
                            "Missing Skills": ", ".join(c["missing_skills"]),
                        })
                        with st.container(border=True):
                            st.markdown(
                                f"**Candidate #{c['candidate_id']}** — "
                                f"Score: **{c['score']:.1f}**"
                            )
                            st.write("Breakdown:", c["breakdown"])
                            st.write("Missing skills:", ", ".join(c["missing_skills"]) or "—")
                            st.write("Extracted:", c.get("structured"))
                    df = pd.DataFrame(df_rows)
                    st.download_button(
                        "⬇️ Download CSV",
                        df.to_csv(index=False),
                        "shortlist.csv",
                        mime="text/csv"
                    )
            else:
                st.error(r.text)
        except Exception as e:
            st.error(f"Request error: {e}")

with tab4:
    st.subheader("Explain a Candidate (LLM Justification)")

    job_id_ex = st.number_input("Job ID", 1, step=1, key="jobid_ex")
    resume_id_ex = st.number_input("Resume ID", 1, step=1, key="resid_ex")

    if st.button("Explain"):
        try:
            r = requests.get(
                f"{API}/match/justify",
                params={"job_id": int(job_id_ex), "resume_id": int(resume_id_ex)},
                timeout=120
            )
            if r.ok:
                data = r.json()
                st.markdown(f"**Fit Score:** {data['score']:.1f}")
                st.write("Breakdown:", data["breakdown"])
                st.write("Missing skills:", ", ".join(data["missing_skills"]) or "—")
                st.divider()
                st.subheader("🤖 LLM Justification")
                st.json(data["justification"])
                st.caption("*(Set LLM_API_BASE and LLM_API_KEY in .env for live LLM — else mock justification)*")
            else:
                st.error(r.text)
        except Exception as e:
            st.error(f"Request error: {e}")

