from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path

# Extract metadata from PDF
def extract_pdf_metadata(file_path):
    reader = PdfReader(file_path)
    metadata = reader.metadata
    num_pages = len(reader.pages)
    return {
        "title": metadata.get("/Title", "Unknown Title"),
        "author": metadata.get("/Author", "Unknown Author"),
        "subject": metadata.get("/Subject", "Unknown Subject"),
        "pages": num_pages
    }

# Check if PDF has embedded text
def has_embedded_text(file_path):
    reader = PdfReader(file_path)
    page = reader.pages[0]
    text = page.extract_text()
    return text.strip() != ""

# Determine if a PDF is scanned using OCR
def is_scanned_pdf(file_path):
    if has_embedded_text(file_path):
        return False

    images = convert_from_path(file_path, first_page=1, last_page=1)
    text = pytesseract.image_to_string(images[0])

    return len(text.strip()) < 100

def contains_financial_tables(pdf_path):
    import pdfplumber
    FINANCIAL_KEYWORDS = ["balance", "income", "revenue", "expenses", "assets", "liabilities", "profit", "loss", "equity", "cash flow"]
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                joined = " ".join([" ".join(row).lower() for row in table if row])
                if any(keyword in joined for keyword in FINANCIAL_KEYWORDS):
                    return True
    return False

def is_legal_document(pdf_path):
    from PyPDF2 import PdfReader
    LEGAL_KEYWORDS = ["agreement", "contract", "party", "jurisdiction", "terms", "whereas", "witnesseth", "confidentiality"]
    reader = PdfReader(pdf_path)
    first_page_text = reader.pages[0].extract_text().lower()
    return any(word in first_page_text for word in LEGAL_KEYWORDS)

