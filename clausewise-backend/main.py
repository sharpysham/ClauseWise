import time
import traceback
import pdfplumber
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ai_engine.engine import analyze_contract

app = FastAPI(title="ClauseWise API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ClauseWise backend is running"}

@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted.")

    contents = await file.read()

    if len(contents) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Max 20MB.")

    start_time = time.time()

    try:
        # Step 1: Extract text from PDF
        print(f"📄 Extracting: {file.filename}")
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            contract_text = "\n".join(p.extract_text() or "" for p in pdf.pages)

        if len(contract_text.strip()) < 50:
            raise HTTPException(status_code=400, detail="Could not extract text. Try a non-scanned PDF.")

        # Step 2: Run AI engine
        print("🧠 Running AI analysis...")
        result = analyze_contract(contract_text)

        # Step 3: Add timing
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        result["processing_time_ms"] = elapsed_ms
        print(f"✅ Done in {elapsed_ms}ms")

        return result

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")