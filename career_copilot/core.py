from __future__ import annotations
import re
from typing import Dict, List, Tuple

SKILL_SYNONYMS = {
    "machine learning": ["ml", "machine-learning"],
    "deep learning": ["dl", "deep-learning"],
    "natural language processing": ["nlp"],
    "large language models": ["llm", "llms", "large language model"],
    "data analysis": ["data analytics", "data analyst"],
    "sql": ["structured query language"],
    "python": ["python programming"],
    "javascript": ["js"],
    "react": ["react.js", "reactjs"],
    "node.js": ["nodejs", "node"],
    "rest api": ["restful api", "apis", "api development"],
    "git": ["github", "version control"],
    "docker": ["containerization", "containers"],
    "aws": ["amazon web services"],
    "communication": ["verbal communication", "written communication"],
    "problem solving": ["analytical thinking", "critical thinking"],
    "tensorflow": ["tf"],
    "pytorch": ["torch"],
    "scikit-learn": ["sklearn"],
    "html": ["html5"],
    "css": ["css3"],
    "c++": ["cpp"],
    "c": ["c programming"],
    "java": ["java programming"],
    "mongodb": ["mongo"],
    "postgresql": ["postgres"],
    "computer networks": ["networking"],
    "operating systems": ["os"],
    "database management": ["dbms", "database management systems"],
}

def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \\t]+", " ", text)
    text = re.sub(r"\\n{3,}", "\\n\\n", text)
    return text.strip()

def extract_pdf_text(uploaded_file) -> str:
    try:
        import fitz
        document = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
        return normalize_text("\\n".join(page.get_text("text") for page in document))
    except Exception as exc:
        raise ValueError(f"Could not read this PDF: {exc}") from exc

def _canonical_skill_mentions(text: str) -> Dict[str, str]:
    low = re.sub(r"\\s+", " ", text.lower())
    found = {}
    for canonical, aliases in SKILL_SYNONYMS.items():
        for term in [canonical] + aliases:
            pattern = r"(?<![a-z0-9+#.])" + re.escape(term.lower()) + r"(?![a-z0-9+#.])"
            if re.search(pattern, low):
                found[canonical] = term
                break
    return found

def extract_skills(text: str) -> List[str]:
    return sorted(_canonical_skill_mentions(text).keys())

def compare_skills(resume_text: str, job_text: str) -> Tuple[List[str], List[str]]:
    required = extract_skills(job_text)
    resume = set(extract_skills(resume_text))
    return [s for s in required if s in resume], [s for s in required if s not in resume]

def semantic_similarity(resume_text: str, job_text: str) -> Tuple[float, str]:
    if not resume_text.strip() or not job_text.strip():
        raise ValueError("Resume and job description must both contain readable text.")
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        vectors = model.encode([resume_text[:12000], job_text[:12000]], normalize_embeddings=True)
        score = float(cosine_similarity([vectors[0]], [vectors[1]])[0][0])
        return max(0.0, min(100.0, score * 100)), "Sentence-Transformer: all-MiniLM-L6-v2"
    except Exception:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
        matrix = vectorizer.fit_transform([resume_text, job_text])
        score = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
        return score * 100, "TF-IDF fallback (sentence-transformer unavailable)"

def _mock_generation(role: str, matched: List[str], missing: List[str]) -> dict:
    focus = missing[:5] or ["strengthening practical project evidence", "role-specific problem solving"]
    learning = [f"Study {s} and complete a small hands-on exercise relevant to {role}." for s in focus]
    questions = [
        f"Explain a project or experience where you applied {s}. What was your contribution and outcome?"
        for s in (matched[:3] or ["a relevant technical skill"])
    ]
    questions += [
        f"What is your approach to solving a practical {role} problem involving {s}?"
        for s in focus[:3]
    ]
    questions += [
        "Describe a time you received difficult feedback. How did you respond?",
        "How do you prioritize tasks when working under a tight deadline?",
    ]
    return {
        "learning_plan": learning,
        "technical_questions": questions[:6],
        "behavioural_questions": questions[-2:],
        "mode": "Built-in fallback (no LLM API key)",
    }

def generate_with_llm(role: str, job_text: str, matched: List[str], missing: List[str]) -> dict:
    import os
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return _mock_generation(role, matched, missing)
    try:
        from openai import OpenAI
        import json
        client = OpenAI(api_key=key)
        prompt = f'''
You are an applicant career-preparation assistant. Use only the supplied context.
Target role: {role}
Required skills evidenced in resume: {matched}
Required skills not clearly evidenced: {missing}
Job description excerpt: {job_text[:5000]}
Return valid JSON with keys learning_plan (array of 4 concise actionable items),
technical_questions (array of 5 role-specific questions), and behavioural_questions
(array of 3 questions). Do not claim the candidate lacks a skill absolutely; say evidence
was not found. Do not invent resume experience.
'''
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.4,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
        )
        result = json.loads(response.choices[0].message.content)
        result["mode"] = f"LLM API ({os.getenv('OPENAI_MODEL', 'gpt-4o-mini')})"
        return result
    except Exception as exc:
        fallback = _mock_generation(role, matched, missing)
        fallback["mode"] = f"Fallback used because LLM API failed: {str(exc)[:180]}"
        return fallback

def build_analysis(resume_text: str, job_text: str, role: str = "Target role") -> dict:
    resume_text, job_text = normalize_text(resume_text), normalize_text(job_text)
    if len(resume_text) < 30:
        raise ValueError("Very little resume text was extracted. Use a text-based PDF; scanned PDFs need OCR.")
    if len(job_text) < 30:
        raise ValueError("Please provide a longer job description (at least a few meaningful lines).")
    score, model_name = semantic_similarity(resume_text, job_text)
    matched, missing = compare_skills(resume_text, job_text)
    generated = generate_with_llm(role, job_text, matched, missing)
    return {
        "score": round(score, 1),
        "embedding_model": model_name,
        "matched_skills": matched,
        "missing_skills": missing,
        "learning_plan": generated.get("learning_plan", []),
        "technical_questions": generated.get("technical_questions", []),
        "behavioural_questions": generated.get("behavioural_questions", []),
        "generation_mode": generated.get("mode", "Unknown"),
        "resume_excerpt": resume_text[:1200],
    }
