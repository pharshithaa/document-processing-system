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

extraction_prompt = """
You are an intelligent document analyst. Analyze the following text carefully and carry out these tasks:

1. **Summarize** the overall content — explain the document's main topic and purpose in a few sentences.
2. **Highlight key sections** such as instructions, summaries, or important details.
3. **Detect and extract any tabular data** (e.g., rows and columns of structured information). Even if the tables are not perfectly formatted, do your best to reconstruct them.
   - Present tables using Markdown with clear headers and rows.
   - Add a brief note describing what each table likely represents.
4. If you are confident that **no structured tables are present**, say: "No tables were detected in this document."

Be formal, avoid assumptions, and format the response clearly.

Document Text:
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

def extract_with_llama(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    prompt = extraction_prompt.format(text=text)
    response = llm.invoke(prompt)
    return {
        "success": True,
        "model": "Llama 3.2",
        "data": str(response)
    }