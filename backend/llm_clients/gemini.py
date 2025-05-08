import os
import base64
import requests
from pdf2image import convert_from_path
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()

# Function to convert scanned PDF to image and extract with Gemini API (for scanned PDFs)
def extract_from_scanned_pdf(pdf_path):
    try:
        # Convert PDF to image(s)
        images = convert_from_path(pdf_path)
        
        # Convert the first page image to base64
        def image_to_base64(img):
            from io import BytesIO
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")

        img_base64 = image_to_base64(images[0])

        API_KEY = os.getenv("GEMINI_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

        payload = {
            "contents": [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": img_base64
                        }
                    },
                    {
                        "text":"""Extract all possible tables, the document title, and any important information from this document.

                            Format your response in **Markdown** using these rules:

                            1. Use `#` for main headings and `##` for subheadings.
                            2. For **tables**:
                            - Extract **all tables**, even small or partial ones.
                            - If structured data appears (e.g., schedules, prices, feature lists), treat it as a table.
                            - Every table should begin with a clear title (e.g., **"Pricing Table"**).
                            - Use proper markdown format with `|` and `-`:
                                ```
                                | Header 1 | Header 2 |
                                |----------|----------|
                                | Data 1   | Data 2   |
                                ```
                            3. Use bullet points for any key insights, lists, or highlights.
                            4. Use `**bold**` for important values or keywords.
                            5. If **no tables** are detected, still summarize the document and return key insights as bullet points.

                            Be precise and do **not invent data**. Always reflect only what is present in the image.
                            Text: {text}
                            """

                    }
                ]
            }]
        }

        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            # Extract just the text content from Gemini's response
            text_content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            return {
                "success": True,
                "model": "gemini-scanned",
                "data": text_content  # Return just the text content
            }
        else:
            return {
                "success": False,
                "model": "gemini-scanned",
                "error": f"API Error: {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "model": "gemini-scanned",
            "error": str(e)
        }

# Function to handle large documents and route them to the correct Gemini model
def extract_from_large_document(pdf_path):
    try:
        # First extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        
        # Define prompt for large document extraction
        large_document_prompt = """
        Extract all possible tables, the document title, and any important information from this document.

            Format your response in **Markdown** using these rules:

            1. Use `#` for main headings and `##` for subheadings.
            2. For **tables**:
            - Extract **all tables**, even small or partial ones.
            - If structured data appears (e.g., schedules, prices, feature lists), treat it as a table.
            - Every table should begin with a clear title (e.g., **"Pricing Table"**).
            - Use proper markdown format with `|` and `-`:
                ```
                | Header 1 | Header 2 |
                |----------|----------|
                | Data 1   | Data 2   |
                ```
            3. Use bullet points for any key insights, lists, or highlights.
            4. Use `**bold**` for important values or keywords.
            6. If **no tables** are detected, still summarize the document and return key insights as bullet points.
            7. Note that if any table is skipped, incomplete, or mentioned but not shown, it will be considered a failure. Show every single table in the best possible Markdown approximation.
            8. **Final Document Summary**
   - After all tables, provide a **clear, concise summary** of what the document reveals overall.
   - Focus on insights such as: *profit/loss*, *trends*, *key performance figures*, or *overall financial health*.
   - Example: "The document indicates a consistent monthly profit, with Q2 outperforming Q1 in revenue."
            9. If possible,show the page number in which the tables occur.
            
            
            Be precise and do **not invent data**. Always reflect only what is present in the image.

        Text: {text}
        """

        API_KEY = os.getenv("GEMINI_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

        payload = {
            "contents": [{
                "parts": [
                    {
                        "text": large_document_prompt.format(text=text)
                    }
                ]
            }]
        }

        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            # Extract just the text content from Gemini's response
            text_content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            return {
                "success": True,
                "model": "gemini-large",
                "data": text_content  # Return just the text content
            }
        else:
            return {
                "success": False,
                "model": "gemini-large",
                "error": f"API Error: {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "model": "gemini-large",
            "error": str(e)
        }

# Main function to determine document type and extract content
def process_document(pdf_path, document_type="scanned"):
    if document_type == "scanned":
        print("Processing as scanned PDF with Gemini...")
        return extract_from_scanned_pdf(pdf_path)
    elif document_type == "large":
        print("Processing as large document with Gemini...")
        return extract_from_large_document(pdf_path)

# Function to extract text from PDF (for large documents)
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def ask_gemini_question(document_text, user_question):
    """
    Given the document text and a user question, use Gemini to answer the question based on the document context.
    """
    API_KEY = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    prompt = f"""
    You are an expert assistant. Use the following document to answer the user's question. Be concise and accurate.
    Instructions:
- Answer ONLY if the information is present in the document.
- If the answer cannot be found in the document, respond with:
  "The document does not contain information about that."
- Do not assume, guess, or invent information.
- Keep the answer clear and concise.

    Document:
    {document_text}

    Question: {user_question}
    """
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt}
            ]
        }]
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        text_content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        return text_content
    else:
        return f"API Error: {response.status_code}"

