import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
import io

# Update this path to where Tesseract is installed on your PC
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_pymupdf(file_bytes: bytes) -> dict[int, str]:
    """Extract text page by page using PyMuPDF"""
    pages = {}
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        pages[page_num + 1] = text.strip()
    return pages

def extract_text_ocr(file_bytes: bytes) -> dict[int, str]:
    """OCR fallback for scanned PDFs"""
    pages = {}
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(img)
        pages[page_num + 1] = text.strip()
    return pages

def extract_pdf_text(file_bytes: bytes) -> dict[int, str]:
    """Try normal extraction first, fall back to OCR if pages are empty"""
    pages = extract_text_pymupdf(file_bytes)
    
    # Check if meaningful text was found
    total_text = " ".join(pages.values())
    if len(total_text.strip()) < 100:
        print("⚠️ Low text detected — switching to OCR fallback")
        pages = extract_text_ocr(file_bytes)
    
    return pages