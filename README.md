# document-processing-system
The frontend is built using *React.js*, offering an intuitive interface for document upload, real-time status tracking, and output display.
Tools and Libraries Used
React.js: The core library for building the user interface. React allows for state-driven updates, making it ideal for handling dynamic content such as real-time status changes.

Material-UI (MUI): A popular UI library that provides a wide range of pre-built components, such as buttons, progress bars, and badges, which help in creating a consistent and aesthetically pleasing UI quickly.

react-dropzone: Used to implement drag-and-drop file uploads, making it more user-friendly to upload documents for processing.

react-query: Manages asynchronous data fetching and caching, allowing the frontend to efficiently fetch, update, and display data without unnecessary re-renders.

react-markdown: A React component that converts markdown content into HTML, making it easy to display extracted content (like tables, summaries, etc.) in a clean and readable format.

Socket.IO (via WebSocket): Real-time communication between the frontend and backend. WebSocket provides continuous updates on the document processing status, allowing the frontend to update the UI instantly.