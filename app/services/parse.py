from pathlib import Path

def txt_to_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")

def pdf_to_text(path: str) -> str:
    try:
        import fitz  # PyMuPDF
    except Exception as e:
        raise RuntimeError(f"PDF parsing requires PyMuPDF (pymupdf). Install it first. Inner: {e}")
    doc = fitz.open(path)
    pages = [page.get_text("text") for page in doc]
    return "\n".join(pages).strip()

def docx_to_text(path: str) -> str:
    try:
        from docx import Document
    except Exception as e:
        raise RuntimeError(f"DOCX parsing requires python-docx. Install it first. Inner: {e}")
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs).strip()

def any_to_text(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext in ["", ".txt"]:
        return txt_to_text(path)
    if ext == ".pdf":
        return pdf_to_text(path)
    if ext in [".docx", ".doc"]:
        # NOTE: .doc is best-effort; python-docx only fully supports .docx
        return docx_to_text(path)
    raise ValueError(f"Unsupported file type: {ext}. Use .txt, .pdf, or .docx")
