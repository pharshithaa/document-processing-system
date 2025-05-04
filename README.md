A full-stack application for document uploading, real-time processing status tracking, and structured data extraction using LLMs and OCR.

## Frontend Implementation – React.js

The frontend of the application is built using **React.js**, providing an intuitive and responsive interface for document uploads, real-time status tracking, and output display.

Tools and Libraries Used
**React.js**: Builds the dynamic UI using a component-based structure and reactive updates.

**Material-UI (MUI)**: Provides pre-designed, customizable UI components like buttons and progress bars for a polished look.

**react-dropzone**: Enables user-friendly drag-and-drop file uploads.

**react-query**: Efficiently manages data fetching, caching, and reactivity.

**react-markdown**: Renders markdown content (e.g., summaries, tables) into readable HTML.

**Socket.IO**: Facilitates real-time status updates from the backend using WebSockets.

### Rationale for Tool Selection

- **React.js**: Chosen for its flexibility in managing state and efficiently updating the UI, ideal for handling dynamic content such as real-time status updates during document processing.

- **Material-UI**: Provides a consistent design and pre-built components, speeding up development and ensuring a responsive, clean interface.

- **react-dropzone**: Selected for seamless file uploads, enabling drag-and-drop or manual file selection, which makes the document upload process more user-friendly.

- **react-query**: Chosen for efficient data fetching, reducing unnecessary re-renders, ensuring optimal performance for real-time updates.

- **react-markdown**: Essential for converting markdown data into structured HTML, ensuring extracted content (e.g., tables, summaries) is cleanly rendered and readable.

- **Socket.IO**: Chosen for real-time communication, allowing the frontend to receive continuous updates on document processing without requiring a page refresh.

### Core Features

- **File Upload**: Users can upload documents via drag-and-drop or manual selection. The upload is processed via the `/upload` API, and `react-dropzone` ensures a smooth user experience.

- **Real-Time Status Dashboard**: Displays the document processing stages: **Uploading → Extracting → Processing → Completed / Failed**. WebSocket provides real-time updates, with polling as a fallback if WebSocket is unavailable.

- **Status Visualization**: Displays color-coded badges for each stage (Uploading, Extracting, Processing, Completed, Failed) and a progress bar to visually track the document’s processing stage.


- **Markdown-Based Output**: Processed results (e.g., extracted tables, summaries) are returned in Markdown format and rendered using `react-markdown` for clean, structured output.

- **Error Handling**: Clear error messages are displayed for unsupported file formats or backend failures. The UI reflects errors with a **Failed** badge and detailed error information.

- **Responsive Design**: The layout is mobile-friendly, adjusting for different screen sizes using **Material-UI’s Grid system** to ensure a consistent user experience across devices.

## Backend Implementation – FastAPI & Processing Logic

The backend of the application uses **FastAPI** for API handling, alongside various libraries for document processing. Language models (LLMs) are used to process documents based on their type and size, with real-time updates sent to the frontend.

#### Tools and Libraries Used:

- **FastAPI**: High-performance framework for building APIs.
- **PyPDF2**: Extracts metadata from PDFs.
- **pdf2image**: Converts PDFs to images for OCR processing.
- **pytesseract**: Extracts text from images using OCR.
- **LangChain**: Routes prompts to different LLMs based on document type/length.
- **Socket.IO (via WebSocket)**: Real-time updates for the frontend.
- **TinyLLaMA**: Lightweight model for small document processing.
- **Gemini**: Large model for handling long documents with an extended context window.
- **Ollama (Ollama 3.2)**: Specialized model for legal and financial document processing.

#### Rationale for Tool Selection:

- **FastAPI**: Chosen for its speed and asynchronous capabilities, making it ideal for handling document processing requests efficiently.
- **PyPDF2** & **pdf2image**: Used to extract metadata and convert PDFs into images for OCR, enabling document processing from scanned PDFs.
- **pytesseract**: Applied to extract text from scanned images/PDFs.
- **LangChain**: Simplifies the integration of multiple LLMs and routes prompts effectively based on document type/size.
- **Socket.IO**: Enables real-time communication, allowing the frontend to receive live updates on document processing status.

#### Model Selection Rationale:

- **TinyLLaMA**: **Cost-effective and fast**, ideal for processing small documents (less than 3 pages).
- **Gemini**: **Best for large documents** (more than 10 pages) because of its extended context window, making it ideal for handling long-form content efficiently.
- **Ollama**: **Specialized in legal and financial documents**, Ollama excels at extracting structured data, like tables, from such documents, while being more affordable than premium models like GPT-4.

#### Cost-Effectiveness Consideration:

**Ollama** and **TinyLLaMA** were selected due to their **cost-effectiveness** compared to models like GPT-4 or Gemini. While these premium models offer powerful capabilities, **Ollama** and **TinyLLaMA** are more affordable and specialized, making them ideal for applications requiring focused processing at a lower cost. This is particularly beneficial for smaller documents or specialized content like **legal** and **financial data**, where the added complexity of higher-end models (like **Gemini**) isn’t necessary.

---

c.Steps to Build and Test the Project
This section outlines how to set up, run, and test the full-stack document processing application on your local machine.

🛠️ 1. Clone the Repository
bash

git clone https://github.com/your-username/document-processing-project.git
cd document-processing-project
🐍 2. Backend Setup (FastAPI)
✅ Create and activate a virtual environment (recommended to avoid dependency conflicts):

bash

# macOS/Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
✅ Install backend dependencies:

bash

pip install -r requirements.txt
✅ Create a .env file in the backend root with the following contents:

env

UPLOAD_DIR=./uploads
LLM_API_KEY=your-llm-api-key
✅ Run the FastAPI server:

bash

uvicorn main:app --reload
Backend will be available at: http://localhost:8000

⚛️ 3. Frontend Setup (React.js)
✅ Navigate to the frontend directory:

bash

cd frontend
✅ Install frontend dependencies:

bash

npm install
✅ Create a .env file in the frontend root with the following contents:

env

REACT_APP_API_URL=http://localhost:8000
✅ Run the React development server:

bash
npm start
Frontend will be available at: http://localhost:3000

🧪 4. Testing the Application
Open your browser and go to: http://localhost:3000

Upload different types of PDF documents

Monitor real-time status updates:

Uploading → Extracting → Processing → Completed

Processed results (summaries, tables, text) will appear in the UI with Markdown formatting.