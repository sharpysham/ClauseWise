# ClauseWise ⚖️

We built this because most people sign contracts without actually understanding them.
Lawyers are expensive. Legal jargon is confusing. ClauseWise tries to fix that.

Upload any legal PDF — rental agreement, internship contract, NDA — and it tells you
what's risky, what's contradictory, and what you should actually care about.

---

## What it does

- Reads your PDF and splits it into individual clauses
- Classifies each clause by risk type (Financial, Termination, Data Privacy, etc.)
- Detects when two clauses in the same document contradict each other
- Explains each risky clause in plain English using an LLM
- Gives every clause a risk level — HIGH, MEDIUM, or LOW

---

## Example of what it catches

A rental agreement that says:
> "The deposit will be refunded within 7 days of vacating."

And then two lines later:
> "The deposit may be retained fully regardless of property condition."

ClauseWise flags both, links them together, and explains exactly why that's a problem.

---

## Tech we used

**Backend**
- FastAPI (Python)
- facebook/bart-large-mnli for zero-shot clause classification
- spaCy for entity extraction (money, durations, percentages)
- ONNX Runtime with INT8 quantization (runs on CPU, optimized for AMD Ryzen)
- Groq API with Llama 3.1 for plain-English explanations
- PyMuPDF + pdfplumber for PDF text extraction

**Frontend**
- React + Vite
- Axios

---

## How to run it

**Backend**
```bash
cd clausewise-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m ai_engine.onnx_export
uvicorn main:app --reload
```

**Frontend**
```bash
cd clausewise-frontend
npm install
npm run dev
```

Add your Groq API key in a `.env` file inside `clausewise-backend/`:
```
GROQ_API_KEY=your_key_here
```

---

## Project structure
```
clausewise-backend/
├── main.py
├── extractor.py
└── ai_engine/
    ├── engine.py
    ├── classifier.py
    ├── segmenter.py
    ├── entity_extractor.py
    ├── risk_scorer.py
    ├── explainer.py
    └── onnx_export.py

clausewise-frontend/
└── src/
    └── App.jsx
```

---

## Known limitations

- Money amounts in Indian Rupee (₹) are sometimes missed by spaCy
- Classification confidence is low on very short or vague clauses
- Processing takes 2–3 minutes on CPU for a full document

---

## Disclaimer

This is a student project. ClauseWise is not a lawyer and does not give legal advice.
Always have a professional review important contracts.



