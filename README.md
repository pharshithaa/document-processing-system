# Document Processing Platform – LLM-Driven PDF Processor

A full-stack application that allows users to upload PDF documents and automatically routes them through specialized LLMs based on their type and size. It supports scanned PDFs (OCR), legal and financial document parsing, and real-time status updates.

# Document Processing Pipeline

```mermaid
graph TD
    %% Frontend Flow
    A[Upload Document] --> B[Initiate WebSocket Connection & Trigger Processing]
    B --> C[Content & Metadata Extraction]
    
    %% Backend Processing
    C --> D[Document Classification & OCR Handling]
    D --> E[Route to Appropriate Model]

    %% Processing Paths
    E -->|Large >10 pages| F[Gemini Model]
    E -->|Financial/Legal| G[Ollama 3.2]
    E -->|Small ≤3 pages| H[TinyLLaMA]
    E -->|Default| I[Ollama 3.2]
    
    %% Content Processing
    F --> J[Process Document & Generate Output]
    G --> J
    H --> J
    I --> J

    
    %% Results & Status
    J --> K[Render Results on Frontend]
    K --> L[WebSocket Termination]
    L --> M[User Asks Custom Question]
    M --> N[LLM Processes Question & Generates Answer]
    N --> O[Display Answer on Frontend]
    

    %% Styling - Professional Blue Theme
    style A fill:#2c3e50,stroke:#34495e,stroke-width:2px,color:#fff
    style B fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    style C fill:#2c3e50,stroke:#34495e,stroke-width:2px,color:#fff
    style D fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    style E fill:#2c3e50,stroke:#34495e,stroke-width:2px,color:#fff
    style F fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    style G fill:#2c3e50,stroke:#34495e,stroke-width:2px,color:#fff
    style H fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    style I fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    style J fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    style K fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    style L fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    style M fill:#2c3e50,stroke:#34495e,stroke-width:2px,color:#fff
    style N fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    style O fill:#2c3e50,stroke:#34495e,stroke-width:2px,color:#fff
```
     
## Frontend Implementation – React.js

The frontend of the application is built using **React.js**, providing an intuitive and responsive interface for:

- Uploading documents  
- Receiving real-time status updates  
- Viewing extracted outputs (tables, summaries)

### Tools and Libraries Used

| Tool/Library       | Purpose                                                         |
| ------------------ | --------------------------------------------------------------- |
| React.js           | Builds dynamic, responsive UI components                        |
| Material-UI        | Provides polished, pre-designed UI components                   |
| react-dropzone     | Enables smooth drag-and-drop or manual file uploads             |
| react-query        | Manages API state, caching, and reactivity for smoother updates |
| react-markdown     | Renders extracted markdown (e.g., tables/summaries) into HTML   |
| WebSocket         | Supports real-time communication between frontend and backend   |

### Rationale for Tool Selection

- **React.js**: Ideal for dynamic UI with real-time updates  
- **Material-UI**: Speeds up styling and maintains a consistent design  
- **react-dropzone**: Provides a user-friendly drag-and-drop interface  
- **react-query**: Optimizes performance with smart caching and re-fetching  
- **react-markdown**: Ensures clean rendering of LLM-generated markdown  
- **WebSocket**: Enables real-time progress tracking by maintaining a persistent connection between frontend and backend

### Core Features

- **File Upload**: Drag-and-drop or manual upload via `react-dropzone`, sent to `/upload`  
- **Real-Time Status Dashboard**: Tracks states (Uploading → Extracting → Processing → Completed/Failed) via WebSocket (or polling fallback)  
- **Progress Visualization**: Color-coded badges and progress bar show live processing status  
- **Markdown Output**: Extracted summaries/tables rendered cleanly using `react-markdown`  
- **Error Handling**: Handles backend failures or unsupported formats with visible feedback
- **Custom Question Answering (LLM-Powered)** : Users can interactively ask **custom questions** about the content

---

## Backend Implementation – FastAPI & LLM Routing

The backend uses **FastAPI** for asynchronous API management and document routing based on type, size, and content using LangChain and multiple LLMs.

### Tools and Libraries Used

| Tool/Library    | Purpose                                                          |
| --------------- | ---------------------------------------------------------------- |
| FastAPI         | Fast, asynchronous API development                               |
| PyPDF2          | Extracts document metadata                                       |
| pdf2image       | Converts PDFs into images for OCR                                |
| pytesseract     | Performs OCR on scanned PDF images                               |
| LangChain       | Routes inputs to appropriate LLM based on rules                  |
| WebSocket       | Sends real-time document status to frontend                      |
| TinyLLaMA       | Efficient model for short documents                              |
| Gemini          | Used for scanned and large documents (multimodal & long context) |
| Ollama 3.2      | Specialized in parsing legal and financial documents             |

### Rationale for Tool Selection

- **FastAPI**: Lightweight, async-capable API ideal for concurrent processing tasks  
- **pdf2image + pytesseract**: Extracts text from scanned images using Tesseract OCR  
- **LangChain**: Central logic to route documents based on size/type to the right LLM  
- **Socket.IO**: Real-time updates pushed to frontend for each processing stage  
- **TinyLLaMA**: Low-latency and cost-efficient for simple documents  
- **Gemini**: Handles complex scanned or large PDFs using its multimodal capability  
- **Ollama**: Efficient at parsing structured and domain-specific data (contracts, tables)

---

## Model Selection Rationale

| Model          | Use Case                              | Why Selected                                                   |
| -------------- | ------------------------------------- | -------------------------------------------------------------- |
| TinyLLaMA      | Short/general documents (≤3 pages)    | Fast, cost-effective for basic content                         |
| Gemini         | Scanned PDFs or Long Docs (>10 pages) | Multimodal + large context window, ideal for long/complex docs |
| Ollama 3.2     | Legal and financial documents         | Specializes in domain-specific structure and table extraction  |

### Cost-Effectiveness Note

While powerful models like GPT-4 or Claude offer advanced features, we prioritized TinyLLaMA and Ollama for their balance of performance and cost-efficiency. These models deliver fast, specialized outputs for smaller or niche documents — avoiding the expense of premium models where unnecessary.

---

## Model Routing Logic

The system uses a rule-based LLM router for optimal model selection. This ensures each document is handled by the most capable and cost-efficient model.

| Check Priority        | Condition                       | Model Used               |
| --------------------- | ------------------------------- | ------------------------ |
| 1. Scanned Document   | Detected via OCR need           | Gemini                   |
| 2. Large Document     | More than 10 pages              | Gemini                   |
| 3. Financial Document | Detected via metadata/text cues | Ollama 3.2               |
| 4. Legal Document     | Detected via keywords/context   | Ollama 3.2               |
| 5. Small Document     | 3 pages or fewer                | TinyLLaMA                |
| 6. Fallback           | All else                        | Ollama 3.2               |

Some models are reused across multiple conditions (e.g., Gemini for both scanned and large documents, Ollama 3.2 for legal, financial, and fallback cases). This is intentional — different prompts and processing logic are applied based on the document context to leverage the model's strengths effectively for each use case.

---

## How It Works (Flow Summary)

1. **User uploads a PDF** via React Dropzone.
2. **Backend saves the file** and begins processing.
3. **WebSocket is established** for real-time status updates.
4. **Scanned PDFs are detected**, and OCR is applied using Tesseract.
5. **Metadata and content are extracted** using PyPDF2.
6. **Document is routed** to the appropriate LLM via LangChain.
7. **Selected model processes the content** and returns structured Markdown.
8. **WebSocket pushes live status updates** to the frontend.
9. **Frontend renders Markdown output** as readable HTML along with metadata.
10. **Terminate WebSocket Connection** after processing is complete.
11. **User can ask custom questions** about the document's content

---
##  UI Preview
![Web Preview](./assets/preview.png)

## Setup and Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/document-processing-system.git
cd document-processing-project
```

### 2. Backend Setup (FastAPI)
```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create `.env` file in backend root:
```env
GEMINI_API_KEY="GEMINI KEY"
HF_TOKEN="HUGGING FACE TOKEN"
```

Run the FastAPI server:
```bash
uvicorn main:app --reload
```
Backend will be available at: http://localhost:8000

### 3. Frontend Setup (React.js)
```bash
cd frontend
npm install
```

Create `.env` file in frontend root:
```env
REACT_APP_API_URL=http://localhost:8000
```

Run the React development server:
```bash
npm start
```
Frontend will be available at: http://localhost:3000

## Testing the Application

1. Open your browser and go to: http://localhost:3000
2. Upload different types of PDF documents
3. Monitor real-time status updates:
   - Uploading → Extracting → Processing → Completed
4. Processed results (summaries, tables, text) will appear in the UI with Markdown formatting
