import os
import fitz  # PyMuPDF for PDF text extraction and metadata
from langchain_ollama.llms import OllamaLLM
from dotenv import load_dotenv
from huggingface_hub import login

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
login(token=HF_TOKEN)

# Initialize Ollama LLM (Llama 3.2 model)
print("Loading Llama 3.2 model from Ollama...")
llm = OllamaLLM(model="llama3.2")

# --------------------- PROMPTS ---------------------
financial_extraction_prompt = """
You are a financial document expert. Your task is to:

1. Provide a brief 2–3 line summary of the financial document.
2. Analyze the content for any financial tables:
   - If **tables are found**:
     - Extract them using **Markdown table format** with **clear column headers and properly aligned rows**.
     - For each table, explain what it likely represents (e.g., income statement, balance sheet).
     - Highlight key financial values such as revenue, profit/loss, assets, liabilities, etc.
   - If **no tables are found**:
     - Still summarize any important financial information or figures mentioned in the text.
     - Clearly state: "No financial tables were found in this document."

Be accurate. Do not fabricate tables. Format all output cleanly and professionally.

Text:
{text}
"""



legal_extraction_prompt = """
You are a legal document analyst. Your task is to:
1. Provide a 2–3 line summary of the legal document.
2. Extract key legal clauses such as:
   - Parties involved
   - Agreement terms
   - Duration
   - Termination, jurisdiction, or confidentiality clauses
3. Format clearly using bullet points or sections.

Text:
{text}
"""

table_extraction_prompt = """
You are a structured data expert. Your task is to analyze the following text and:

1. **Check if there are any tables** in the content.
2. If tables are found:
   - Extract and format them clearly using Markdown (with proper headers and rows).
   - Mention briefly what each table likely represents (e.g., pricing, schedule).
3. If **no tables are found**, do NOT invent any. Instead:
   - Return a short summary of the document.
   - Clearly state: "No tables were detected in this document."

Be precise. Do not fabricate tables. Use professional and clear formatting.

Text:
{text}
"""


# --------------------- METADATA FUNCTIONS ---------------------

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num, page in enumerate(doc, 1):
        text += f"\n--- Page {page_num} ---\n"
        text += page.get_text()
    return text

# --------------------- MAIN EXTRACTORS ---------------------

def extract_financial_data_with_llama(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    prompt = financial_extraction_prompt.format(text=text)
    response = llm.invoke(prompt)
    return {
        "success": True,
        "model": "Llama 3.2",
        "data": str(response)
    }

def extract_legal_data_with_llama(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    prompt = legal_extraction_prompt.format(text=text)
    response = llm.invoke(prompt)
    return {
        "success": True,
        "model": "Llama 3.2",
        "data": str(response)
    }

def extract_tables_with_llama(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    prompt = table_extraction_prompt.format(text=text)
    response = llm.invoke(prompt)
    return {
        "success": True,
        "model": "Llama 3.2",
        "data": str(response)
    }