import React, { useState, useEffect, useCallback, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useDropzone } from 'react-dropzone';
import { useMutation } from '@tanstack/react-query';
import StatusDashboard from './StatusDashboard';
import './FileUpload.css';
import './FollowupQA.css';


const API_BASE_URL = 'http://localhost:8000';
const UPLOAD_URL = `${API_BASE_URL}/api/upload/`;
const WS_BASE_URL = 'ws://localhost:8000';

const FileUpload = () => {
    const [files, setFiles] = useState([]); // [{ file, name, size, status, progress, result, error, ws }]
    const [selectedIdx, setSelectedIdx] = useState(null);
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [isAsking, setIsAsking] = useState(false);

    // Handle file selection (drag-and-drop or click)
    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles && acceptedFiles.length > 0) {
            const newFiles = acceptedFiles.map(file => ({
                file,
                name: file.name,
                size: (file.size / 1024).toFixed(2) + ' KB',
                status: 'Started',
                progress: 0,
                result: null,
                error: null,
                ws: null,
                isProcessing: false
            }));
            setFiles(prev => [...prev, ...newFiles]);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        multiple: true,
        accept: {
            'application/pdf': ['.pdf']
        },
        disabled: false
    });

    // Upload mutation using React Query
    const uploadMutation = useMutation({
        mutationFn: async ({ file, idx }) => {
            const formData = new FormData();
            formData.append('file', file);
            const response = await fetch(UPLOAD_URL, {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) {
                throw new Error('Upload failed');
            }
            return response.json();
        },
        onSuccess: (data, { idx }) => {
            updateFile(idx, { result: data, isProcessing: false });
        },
        onError: (error, { idx }) => {
            updateFile(idx, { status: 'Failed', error: error.message, isProcessing: false });
        }
    });

    // Upload all files that are not yet started
    const handleUploadAll = () => {
        console.log('Upload All clicked. Files:', files);
        files.forEach((f, idx) => {
            console.log(`Checking file ${idx}:`, f);
            // Only upload files that haven't completed
            if (f.status !== 'Completed') {
                console.log(`Starting upload for file ${idx}:`, f.name);
                // Close any existing WebSocket connection
                if (f.ws) {
                    f.ws.close();
                }
                // Reset the file status and start fresh
                updateFile(idx, { 
                    status: null, 
                    progress: 0, 
                    error: null, 
                    isProcessing: false,
                    result: null
                });
                uploadFile(f, idx);
            } else {
                console.log(`Skipping completed file ${idx}:`, f.name);
            }
        });
    };

    // Upload a single file
    const uploadFile = async (fileObj, idx) => {
        updateFile(idx, { status: 'Started', progress: 0, error: null, isProcessing: true });
        
        // First establish WebSocket connection using filename
        const wsConnection = new WebSocket(`${WS_BASE_URL}/ws/status/${fileObj.name}`);
        wsConnection.onopen = () => {
            console.log('WebSocket connected for file:', fileObj.name);
            // Only start upload after WebSocket is connected
            uploadMutation.mutate({ file: fileObj.file, idx });
        };
        wsConnection.onmessage = (event) => {
            console.log('Received WebSocket message:', event.data);
            const status = event.data;
            let progress = 10;
            switch(status) {
                case 'Uploading': progress = 20; break;
                case 'Extracting': progress = 40; break;
                case 'Processing': progress = 60; break;
                case 'Extracted': progress = 80; break;
                case 'Completed': progress = 100; break;
                case 'Failed': progress = 0; break;
                default: break;
            }
            let isProcessing = !(status === 'Completed' || status === 'Failed' || status === 'Stopped');
            updateFile(idx, { status, progress, isProcessing });

            // Close WebSocket connection if processing is complete
            if (status === 'Completed' || status === 'Failed' || status === 'Stopped') {
                console.log('Closing WebSocket connection for file:', fileObj.name);
                wsConnection.close();
            }
        };
        wsConnection.onclose = () => {
            console.log('WebSocket closed for file:', fileObj.name);
        };
        wsConnection.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateFile(idx, { status: 'Failed', error: 'WebSocket error', isProcessing: false });
            wsConnection.close();
        };
        updateFile(idx, { ws: wsConnection });
    };

    // Helper to update a file in the array
    const updateFile = (idx, updates) => {
        setFiles(prev => prev.map((f, i) => i === idx ? { ...f, ...updates } : f));
    };

    // Remove a file
    const handleRemove = (idx) => {
        if (files[idx].ws) files[idx].ws.close();
        setFiles(prev => prev.filter((_, i) => i !== idx));
        if (selectedIdx === idx) setSelectedIdx(null);
    };

    // Cancel upload/processing for a file
    const handleCancel = (idx) => {
        if (files[idx].ws) files[idx].ws.close();
        updateFile(idx, { status: 'Stopped', progress: 0, isProcessing: false });
    };

    const resultSectionRef = useRef(null);

    // Cleanup all websockets on unmount
    useEffect(() => {
        return () => {
            files.forEach(f => { if (f.ws) f.ws.close(); });
        };
        // eslint-disable-next-line
    }, []);

    useEffect(() => {
        if (
            selectedIdx !== null &&
            files[selectedIdx] &&
            files[selectedIdx].result &&
            resultSectionRef.current
        ) {
            resultSectionRef.current.scrollIntoView({ behavior: 'smooth' });
        }
        // eslint-disable-next-line
    }, [selectedIdx, files]);

    const handleAskQuestion = async () => {
        if (!question || selectedIdx === null || !files[selectedIdx]?.name) return;
        setIsAsking(true);
        setAnswer('');
        try {
            const res = await fetch('http://localhost:8000/api/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    document_id: files[selectedIdx].name,
                    question: question
                })
            });
            const data = await res.json();
            setAnswer(data.answer || data.error || 'No answer received.');
        } catch (err) {
            setAnswer('Error contacting server.');
        }
        setIsAsking(false);
    };

    return (
        <div className="file-upload-container">
            <div className="header">
                <h1>Document Processor</h1>
                <p>Upload, process & analyze documents effortlessly.</p>
            </div>
            <div className="top-row">
                <div className="upload-card main-content">
                    <h2 className="upload-heading">Upload Documents</h2>
                    <div className="upload-section">
                        <div
                            {...getRootProps()}
                            className={`dropzone ${isDragActive ? 'active' : ''}`}
                        >
                            <input {...getInputProps()} />
                            <div className="dropzone-content">
                                <div className="upload-icon">
                                    <svg width="48" height="48" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M24 34V14m0 0l-8 8m8-8l8 8" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><rect x="4" y="38" width="40" height="6" rx="3" fill="#E5E7EB"/></svg>
                                </div>
                                <div className="dropzone-title">Upload Document</div>
                                <div className="dropzone-subtitle">Drag & drop your files here or click to browse</div>
                                <div className="dropzone-formats">Supported format: PDF(Max: 10MB)</div>
                            </div>
                        </div>
                    </div>
                    <button onClick={handleUploadAll} disabled={files.length === 0} className="upload-button" style={{ marginTop: 16 }}>
                        Upload All
                    </button>
                    <ul className="file-upload-list">
                        {files.map((f, idx) => (
                            <li key={f.name + idx} className="file-upload-card">
                                <div className="file-upload-card-header">
                                    <div className="file-upload-card-info">
                                        <span className="file-icon">
                                            <svg width="24" height="24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6 2a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8.828A2 2 0 0 0 19.414 7.414l-4.828-4.828A2 2 0 0 0 13.172 2H6zm7 1.414L18.586 9H15a2 2 0 0 1-2-2V3.414zM6 4h6v3a4 4 0 0 0 4 4h3v11a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" fill="#3B82F6"/></svg>
                                        </span>
                                        <span className="file-name">{f.name}</span>
                                        <span className="file-size">({f.size})</span>
                                    </div>
                                    <div>
                                        <span className={`status-badge status-${f.status || 'Pending'}`}>
                                            {f.status || 'Pending'}
                                        </span>
                                        <button 
                                            className="remove-file-btn"
                                            onClick={() => handleRemove(idx)}
                                        >
                                            ×
                                        </button>
                                    </div>
                                </div>
                                <div className="progress-container">
                                    <div 
                                        className="progress-bar"
                                        style={{ width: `${f.progress}%` }}
                                    />
                                </div>
                                <div className="file-upload-card-actions">
                                    <button
                                        className="upload-button"
                                        onClick={() => uploadFile(f, idx)}
                                        disabled={f.isProcessing || f.status === 'Completed'}
                                    >
                                        {f.status === 'Completed' ? 'Re-upload' : 'Upload'}
                                    </button>
                                    {f.isProcessing && (
                                        <button
                                            className="cancel-button"
                                            onClick={() => handleCancel(idx)}
                                        >
                                            Cancel
                                        </button>
                                    )}
                                    <button
                                        className="upload-button"
                                        onClick={() => setSelectedIdx(idx)}
                                        disabled={!f.result}
                                    >
                                        View
                                    </button>
                                </div>
                                {f.error && <div className="error-message">Error: {f.error}</div>}
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="dashboard-card">
                    <StatusDashboard files={files} />
                </div>
            </div>
            {selectedIdx !== null && files[selectedIdx] && files[selectedIdx].result && (
                <div className="result-section" ref={resultSectionRef}>
                    <h3>Result for: {files[selectedIdx].name}</h3>
                    <div style={{ marginBottom: 12, color: '#64748b', fontSize: '1.01em' }}>
                        You can ask custom questions about this document below!
                    </div>
                    <button
                        className="upload-button"
                        style={{ marginBottom: 12 }}
                        onClick={() => {
                            // Scroll to the question box
                            document.querySelector('.followup-qa')?.scrollIntoView({ behavior: 'smooth' });
                        }}
                    >
                        Ask a Question
                    </button>
                    <div className="metadata">
                        <strong>Metadata:</strong>
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {`
Title: ${files[selectedIdx]?.result?.metadata?.title || 'N/A'}
Author: ${files[selectedIdx]?.result?.metadata?.author || 'N/A'}
Subject: ${files[selectedIdx]?.result?.metadata?.subject || 'N/A'}
Pages: ${files[selectedIdx]?.result?.metadata?.pages || 'N/A'}
                            `}
                        </ReactMarkdown>
                    </div>
                    <div className="processing-type">
                        <strong>Processing Type:</strong> {files[selectedIdx].result.processing_type}
                    </div>
                    <div className="model">
                        <strong>Model:</strong> {files[selectedIdx].result.model}
                    </div>
                    <div className="results-content">
                        {typeof files[selectedIdx].result.results === 'string' ? (
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {files[selectedIdx].result.results}
                            </ReactMarkdown>
                        ) : (
                            <pre>{JSON.stringify(files[selectedIdx].result.results, null, 2)}</pre>
                        )}
                    </div>
                    <div className="followup-qa" style={{ marginTop: 24 }}>
                        <h4>Ask a follow-up question about this document:</h4>
                        <input
                            type="text"
                            value={question}
                            onChange={e => setQuestion(e.target.value)}
                            placeholder="Type your question..."
                            style={{ width: '70%', marginRight: 8 }}
                            disabled={isAsking}
                        />
                        <button onClick={handleAskQuestion} disabled={isAsking || !question}>
                            {isAsking ? 'Asking...' : 'Ask'}
                        </button>
                        {answer && (
                            <div className="answer" style={{ marginTop: 12, background: '#f3f4f6', padding: 12, borderRadius: 8 }}>
                                <strong>Answer:</strong> {answer}
                            </div>
                        )}
                    </div>
                    <button className="upload-button" onClick={() => setSelectedIdx(null)} style={{ marginTop: 12 }}>
                        Close
                    </button>
                </div>
            )}
        </div>
    );
};

export default FileUpload;
