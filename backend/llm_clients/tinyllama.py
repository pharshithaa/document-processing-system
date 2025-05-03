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
    return result[0]["generated_text"]

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num, page in enumerate(doc, 1):
        text += f"\n--- Page {page_num} ---\n"
        text += page.get_text()
    return text

def extract_tables(text):
    prompt = f"Extract any tables from this text and present them clearly with headers:\n\n{text}"
    print("Calling TinyLlama...\n")
    return call_tinyllama(prompt)


