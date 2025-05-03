import os
import requests
import json
from PyPDF2 import PdfReader
def extract_text_from_file(file_path):
    """
    Extracts plain text from a .pdf or .txt file.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file type. Only .pdf and .txt are supported.")


def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ''
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return text.strip()


def extract_text_from_txt(file_path):
    text = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"TXT extraction error: {e}")
    return text.strip()

def extract_job_info_with_deepseek(text):
    api_url = "https://api.deepseek.com/v1/chat/completions"  # Replace with actual endpoint
    headers = {
        "Authorization": "Bearer sk-f1912bad343f473daad78c989c517f05",       # <-- Replace or use env var
        "Content-Type": "application/json"
    }

    prompt = f"""
    Analyze the following job description and extract structured data:

    \"\"\"{text}\"\"\"

    Return a JSON in this format:
    {{
        "description": "A concise 2–3 sentence summary of the job role",
      "skills": [...],
      "education_levels": [...],
      "experience": "...",
      "tools": [...]
    }}

    Only return the JSON. No explanation.
    """

    payload = {
        "model": "deepseek-chat",  # Use correct model name from their docs
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]

        # Extract JSON block from content
        import re
        match = re.search(r'{.*}', content, re.DOTALL)
        if not match:
            print("No JSON found in DeepSeek response.")
            return []

        raw_data = json.loads(match.group(0))

        # Convert to array of {field, value}
        result = [{"field": key, "value": value} for key, value in raw_data.items()]
        return result

    except Exception as e:
        print("DeepSeek API error:", e)
        return []
    
def score_cv_against_job(cv, job):
    cv_keywords = set(cv.skills + cv.education_levels + cv.tools)
    job_keywords = set(job.skills + job.education_levels + job.tools)

    matched = cv_keywords & job_keywords
    missing = job_keywords - cv_keywords
    score = len(matched) / len(job_keywords) if job_keywords else 0.0

    return round(score * 100, 2), json.dumps(list(matched)), json.dumps(list(missing))
