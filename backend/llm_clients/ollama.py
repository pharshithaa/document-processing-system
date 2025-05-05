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
- If **tables are found**:
     - Extract full tables using **Markdown table format** with **clear column headers and properly aligned rows**.
     - For each table, explain what it likely represents (e.g., income statement, balance sheet).
     - Highlight key financial values such as revenue, profit/loss, assets, liabilities, etc.
     - Ensure the table is **complete**. If there is incomplete data, clearly mention which parts are missing.
   
- If **no tables are found**:
     - Still summarize any important financial information or figures mentioned in the text.
     - Clearly state: "No financial tables were found in this document."

Be accurate. Do not fabricate tables. Format all output cleanly and professionally, ensuring the data is as complete as possible and clearly explained.

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
You are an intelligent and precise document analyst. Read the following document text carefully and perform the following tasks in order:

1. **Summary**: Provide a concise summary of the document. Focus on the main topic and overall purpose.

2. **Key Highlights**: Identify and clearly list the most important sections, such as instructions, summaries, warnings, or critical points. Use bullet points if necessary.

3. **Table Extraction**: Check if the text contains any tabular data (e.g., lists with rows and columns). If found:
   - Reconstruct the tables using **Markdown format** with proper headers and rows.
   - Provide a **brief description** of what each table represents.

4. **Table Absence**: If no tables are detected, write clearly:  
   `"No tables were detected in this document."`

Be objective, avoid assumptions, and format the response clearly with proper headings.

---

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