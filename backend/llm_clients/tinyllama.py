import os
import fitz  # PyMuPDF
from transformers import pipeline
from huggingface_hub import login
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
login(token=HF_TOKEN)

# Load TinyLlama
print("Loading TinyLlama model...")
llm = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")

def call_tinyllama(prompt):
    result = llm(prompt, max_new_tokens=300, do_sample=True)
    generated = result[0]["generated_text"]
    
    # Remove the prompt from the output
    cleaned = generated.replace(prompt, "").strip()
    return cleaned

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num, page in enumerate(doc, 1):
        text += f"\n--- Page {page_num} ---\n"
        text += page.get_text()
    return text

def process_small_document(pdf_path):
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        
        # Create a prompt for small document processing
        prompt = f"""You are a document analyst. Your task is to:

1. Provide a **brief summary** of the document.
2. Identify and extract the **sections** in the document (like "Introduction", "Text Formatting Examples", "Lists").
3. Convert each section into **bullet points** (e.g., key items, formatting, or points mentioned).
4.Do not diaply any page numbers.
Document text:
{text}
"""

        print("Processing small document with TinyLlama...")
        result = call_tinyllama(prompt)
        
        return {
            "success": True,
            "model": "TinyLlama",
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "model": "TinyLlama",
            "error": str(e)
        }


