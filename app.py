from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from matcher import match_resume
from parser import SUPPORTED_EXTENSIONS, extract_text, get_extension

load_dotenv()

app = FastAPI(title="Smart Resume Screening System", version="1.0.0")


class MatchResult(BaseModel):
    filename: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_years: Optional[float] = None
    explanation: str


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()


@app.post("/match-resumes", response_model=List[MatchResult])
async def match_resumes(
    job_description: str = Form(...),
    resumes: List[UploadFile] = File(...),
):
    if not job_description.strip():
        raise HTTPException(400, "job_description must not be empty.")

    results = []
    for resume in resumes:
        ext = get_extension(resume.filename or "")
        if ext not in SUPPORTED_EXTENSIONS:
            raise HTTPException(400, f"Unsupported file type for '{resume.filename}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}")

        content = await resume.read()
        text = extract_text(resume.filename, content)
        outcome = match_resume(job_description, text)
        results.append(MatchResult(filename=resume.filename, **outcome))

    results.sort(key=lambda r: r.match_score, reverse=True)
    return results
