import io
import re

import pdfplumber
from docx import Document

SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt"}


def get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def extract_text_from_pdf(content: bytes) -> str:
    parts = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                parts.append(page_text)
    return "\n".join(parts)


def extract_text_from_docx(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    return "\n".join(p.text for p in doc.paragraphs if p.text)


def extract_text_from_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")


def extract_text(filename: str, content: bytes) -> str:
    ext = get_extension(filename)
    if ext == "pdf":
        raw = extract_text_from_pdf(content)
    elif ext == "docx":
        raw = extract_text_from_docx(content)
    elif ext == "txt":
        raw = extract_text_from_txt(content)
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Supported: {sorted(SUPPORTED_EXTENSIONS)}")
    return re.sub(r"\n{3,}", "\n\n", raw).strip()
