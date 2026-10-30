# AI Career Copilot

**AI Career Copilot: An Intelligent Resume Analysis, Job Matching and Interview Preparation System Using Large Language Models**

B.M.S. College of Engineering · Natural Language Processing for LLM · 24AM7PCLLM

**Team:** Suniksha Priya (1BM23AI192) and Tejas B Raju (1BM23AI196), Semester 7-C.

## Features
- Upload a resume PDF and extract selectable text using PyMuPDF.
- Paste a job description or upload it as a PDF.
- Compare resume and job description using sentence embeddings and cosine similarity.
- Detect skills evidenced in the resume and skills not clearly evidenced using a curated vocabulary and synonym map.
- Generate a targeted learning plan and technical/behavioural interview questions.
- Download a PDF analysis summary.

## Quick start

Python 3.10 or 3.11 is recommended.

### macOS / Linux
```bash
git clone https://github.com/sunikshaai23/AI-Career-Copilot.git
cd AI-Career-Copilot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

### Windows PowerShell
```powershell
git clone https://github.com/sunikshaai23/AI-Career-Copilot.git
cd AI-Career-Copilot
py -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

The app opens at http://localhost:8501.

## Optional live LLM generation
Add your own API key to `.env`:
```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```
Restart Streamlit after editing the file. Never commit `.env` or share your API key.

Without a key, a clearly labelled built-in fallback keeps the complete demo workflow usable. This fallback is deterministic template generation, **not** an LLM.

## Faculty demo
Use the included files:
- Resume: `demo/sample_resume.pdf`
- Job description: `demo/sample_job_description.txt`

1. Start the app.
2. Upload the sample resume.
3. Set role to **Machine Learning Intern**.
4. Paste the sample job description.
5. Click **Analyse my resume**.
6. Review similarity, skill evidence, learning plan and interview questions.
7. Download the PDF report.

See [DEMO_GUIDE.md](DEMO_GUIDE.md) for the presentation walkthrough.

## Architecture
1. **Streamlit UI** — uploads, job input, results and export.
2. **Document processing** — PDF extraction, cleaning and validation.
3. **Semantic matching** — Sentence Transformers and cosine similarity.
4. **Skill analysis** — normalized skill vocabulary and evidence checks.
5. **LLM generation** — learning recommendations and interview questions.
6. **Evaluation and safety** — input validation, limitations and privacy notice.

## Technical notes and limitations
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`.
- If the transformer model cannot be downloaded or loaded, the app uses a labelled TF-IDF fallback for similarity.
- The skill vocabulary is curated and may miss synonyms, transferable skills or contextual evidence.
- Scanned PDFs require OCR; OCR is not included.
- The similarity indicator is **not** an employment probability or a candidate-quality verdict.
- The system supports applicants' preparation; it is not an automated hiring/rejection tool.
- The app does not persist uploaded resumes intentionally. Review privacy and hosting configuration before public deployment.

## Project structure
```text
AI-Career-Copilot/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── DEMO_GUIDE.md
├── career_copilot/
│   ├── __init__.py
│   └── core.py
└── demo/
    ├── sample_resume.pdf
    └── sample_job_description.txt
```
