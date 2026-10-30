import io
from dotenv import load_dotenv
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from career_copilot.core import extract_pdf_text, build_analysis

load_dotenv()
st.set_page_config(page_title="AI Career Copilot", page_icon="🎯", layout="wide")
st.markdown("""
<style>
.main {background:#fbfcff;}
.block-container {padding-top:2rem; max-width:1200px;}
.hero {padding:1.4rem 1.7rem; border-radius:16px; background:linear-gradient(110deg,#102b50,#315d91); color:white;}
.hero h1 {color:white; margin:0 0 .35rem 0;}
.hero p {color:#e8eff8; margin:0;}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>AI Career Copilot</h1><p>Resume analysis · Semantic job matching · Skill-gap insights · Interview preparation</p></div>', unsafe_allow_html=True)
st.write("")
st.caption("B.M.S. College of Engineering | Natural Language Processing for LLM | 24AM7PCLLM")
st.caption("Suniksha Priya (1BM23AI192) and Tejas B Raju (1BM23AI196) | Semester 7-C")

with st.sidebar:
    st.header("How it works")
    st.write("1. Upload your resume PDF")
    st.write("2. Paste the target job description")
    st.write("3. Run semantic matching and skill analysis")
    st.write("4. Review learning suggestions and interview questions")
    st.divider()
    st.caption("Files are processed for this session and are not intentionally saved by this app.")
    st.caption("The match score is a text-similarity indicator, not a hiring probability.")

left, right = st.columns([1, 1])
with left:
    st.subheader("1. Upload resume")
    resume_file = st.file_uploader("Choose a resume PDF", type=["pdf"], key="resume")
with right:
    st.subheader("2. Target role")
    role = st.text_input("Job title / target role", placeholder="e.g. Machine Learning Intern")
    job_file = st.file_uploader("Optional: upload job description PDF", type=["pdf"], key="job")
    job_text_input = st.text_area("Or paste the job description", height=210,
        placeholder="Paste responsibilities, required skills, qualifications, and experience...")

job_text = job_text_input.strip()
if job_file is not None:
    try:
        extracted_job = extract_pdf_text(job_file)
        if extracted_job:
            job_text = extracted_job
            st.success("Job description PDF text extracted. It will be used for analysis.")
        else:
            st.warning("No selectable text found in the job PDF. Paste the job description instead.")
    except Exception as exc:
        st.error(str(exc))

if st.button("Analyse my resume", type="primary", use_container_width=True):
    if resume_file is None:
        st.error("Please upload your resume PDF.")
    elif not job_text:
        st.error("Please paste a job description or upload a readable job-description PDF.")
    else:
        with st.spinner("Extracting text, generating embeddings and analysing skills..."):
            try:
                resume_text = extract_pdf_text(resume_file)
                result = build_analysis(resume_text, job_text, role.strip() or "Target role")
                st.session_state["analysis_result"] = result
                st.session_state["role"] = role.strip() or "Target role"
            except Exception as exc:
                st.error(str(exc))

result = st.session_state.get("analysis_result")
if result:
    st.divider()
    st.header("3. Analysis results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Semantic match indicator", f"{result['score']}%")
    c2.metric("Skills evidenced", len(result["matched_skills"]))
    c3.metric("Skills not clearly evidenced", len(result["missing_skills"]))
    st.progress(min(1.0, max(0.0, result["score"] / 100)))
    st.caption(f"Representation used: {result['embedding_model']}. This score measures textual similarity only; it is not a probability of getting hired.")
    st.caption(f"Generation: {result['generation_mode']}")

    a, b = st.columns(2)
    with a:
        st.subheader("Matched skills")
        if result["matched_skills"]:
            for skill in result["matched_skills"]:
                st.success(skill)
        else:
            st.info("No skills from the curated vocabulary were detected in both texts.")
    with b:
        st.subheader("Skills not clearly evidenced")
        if result["missing_skills"]:
            for skill in result["missing_skills"]:
                st.warning(skill)
        else:
            st.success("All detected required skills were found in the resume text.")

    st.subheader("4. Recommended learning plan")
    for i, item in enumerate(result["learning_plan"], 1):
        st.write(f"**{i}.** {item}")

    q1, q2 = st.columns(2)
    with q1:
        st.subheader("5. Technical interview questions")
        for i, question in enumerate(result["technical_questions"], 1):
            st.write(f"**{i}.** {question}")
    with q2:
        st.subheader("6. Behavioural interview questions")
        for i, question in enumerate(result["behavioural_questions"], 1):
            st.write(f"**{i}.** {question}")

    with st.expander("View extracted resume text (preview)"):
        st.text(result["resume_excerpt"])

    def make_pdf(data, target):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("AI Career Copilot - Resume Analysis", styles["Title"]),
            Spacer(1, 8),
            Paragraph(f"Target role: {target}", styles["Normal"]),
            Paragraph(f"Semantic similarity indicator: {data['score']}%", styles["Heading2"]),
            Paragraph(f"Embedding method: {data['embedding_model']}", styles["Normal"]),
            Paragraph("Note: this is not an employment probability.", styles["Italic"]),
            Spacer(1, 12),
        ]
        sections = [
            ("Matched skills", "matched_skills"),
            ("Skills not clearly evidenced", "missing_skills"),
            ("Learning recommendations", "learning_plan"),
            ("Technical interview questions", "technical_questions"),
            ("Behavioural interview questions", "behavioural_questions"),
        ]
        for heading, key in sections:
            story.append(Paragraph(heading, styles["Heading2"]))
            values = data[key] or ["None identified."]
            for i, value in enumerate(values, 1):
                story.append(Paragraph(f"{i}. {value}", styles["BodyText"]))
            story.append(Spacer(1, 8))
        doc.build(story)
        return buffer.getvalue()

    pdf_bytes = make_pdf(result, st.session_state.get("role", "Target role"))
    st.download_button("Download analysis report (PDF)", data=pdf_bytes,
        file_name="AI_Career_Copilot_Analysis.pdf", mime="application/pdf", type="primary")

st.divider()
st.caption("Educational and career-preparation prototype. Skill matching uses a curated vocabulary and may miss synonyms or transferable experience. Review all generated suggestions.")
