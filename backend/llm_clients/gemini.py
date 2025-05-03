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
                        "text": """Extract all tables, the title, and any important information from this document.
                        Format your response in Markdown with the following rules:
                        1. Use # for main headings and ## for subheadings
                        2. For tables:
                           - Each table must start with a clear title
                           - Use proper markdown table format with | and - characters
                           - Ensure there's a header row and separator row
                           - Example:
                             | Header 1 | Header 2 |
                             |----------|----------|
                             | Data 1   | Data 2   |
                        3. Use bullet points for lists
                        4. Use bold (**) for emphasis
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
        Extract key insights, tables, and summaries from the following text. 
        Format your response in Markdown with the following rules:
        1. Use # for main headings and ## for subheadings
        2. For tables:
           - Each table must start with a clear title
           - Use proper markdown table format with | and - characters
           - Ensure there's a header row and separator row
           - Example:
             | Header 1 | Header 2 |
             |----------|----------|
             | Data 1   | Data 2   |
        3. Use bullet points for lists
        4. Use bold (**) for emphasis

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

