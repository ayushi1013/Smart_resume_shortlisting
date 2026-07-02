import json
import os

from groq import Groq

MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are an expert technical recruiter and resume screener.
Given a job description and a candidate resume, evaluate how well the resume matches the job's requirements.
Respond with STRICT JSON only (no markdown, no extra text), in this exact format:

{
  "match_score": integer 0-100,
  "matched_skills": [list of required skills the resume demonstrates],
  "missing_skills": [list of required skills the resume is missing],
  "experience_years": number or null,
  "explanation": "2-3 sentence explanation of the score"
}"""


def match_resume(job_description: str, resume_text: str) -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"JOB DESCRIPTION:\n{job_description.strip()}\n\nRESUME:\n{resume_text.strip()}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    data = json.loads(response.choices[0].message.content)

    return {
        "match_score": round(float(data["match_score"]), 2),
        "matched_skills": data["matched_skills"],
        "missing_skills": data["missing_skills"],
        "experience_years": data.get("experience_years"),
        "explanation": data["explanation"],
    }
