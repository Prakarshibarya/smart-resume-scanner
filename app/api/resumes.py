import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.db import SessionLocal
from app.models.resume import Resume
from app.services.parse import any_to_text
from app.services.extract import extract_structured
from app.services.embed import embed_text

router = APIRouter()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        suffix = "." + file.filename.split(".")[-1] if "." in file.filename else ".txt"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {e}")

    try:
        raw = any_to_text(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=415, detail=str(e))

    structured = extract_structured(raw) 
    emb = embed_text(raw)

    db = SessionLocal()
    r = Resume(candidate_name=None, raw_text=raw, structured=structured, embedding=emb)
    db.add(r); db.commit(); db.refresh(r)

    preview = (raw[:400] + "...") if raw and len(raw) > 400 else raw
    return {
        "resume_id": r.id,
        "chars": len(raw or ""),
        "preview": preview,
        "structured": structured,  
    }
