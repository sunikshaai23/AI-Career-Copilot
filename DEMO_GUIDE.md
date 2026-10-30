# Faculty Demo Guide

## Demo inputs
- Resume: `demo/sample_resume.pdf`
- Job description: `demo/sample_job_description.txt`

The sample candidate is fictional and created only for demonstration.

## Live demonstration sequence (3–5 minutes)
1. Start the app using `streamlit run app.py`.
2. Upload `demo/sample_resume.pdf`.
3. Enter target role: `Machine Learning Intern`.
4. Open `demo/sample_job_description.txt`, copy its contents and paste into the job description box.
5. Click **Analyse my resume**.
6. Explain the semantic similarity indicator and its model/fallback label.
7. Show matched skills and skills not clearly evidenced.
8. Explain the learning recommendations and technical/behavioural interview questions.
9. Download the generated PDF report.

## Explain the core
- PyMuPDF extracts selectable text from the resume PDF.
- Sentence Transformers (`all-MiniLM-L6-v2`) generates dense text embeddings.
- Cosine similarity compares resume and job-description embeddings.
- A curated skill vocabulary and synonym map identifies skill evidence and potential gaps.
- If an OpenAI API key is configured, an LLM generates tailored learning recommendations and questions.
- Without a key, the app uses a clearly labelled deterministic fallback; this is not an LLM.

## Academic honesty
The match score is a text-similarity indicator, not a hiring probability. The sample data is synthetic. Record actual observations from your execution; do not present illustrative or unmeasured values as experimental results.
