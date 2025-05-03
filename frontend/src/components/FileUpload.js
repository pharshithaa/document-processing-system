import React, { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useDropzone } from 'react-dropzone';
import StatusDashboard from './StatusDashboard';
import './FileUpload.css';

const API_BASE_URL = 'http://localhost:8000';
const UPLOAD_URL = `${API_BASE_URL}/api/upload/`;
const WS_BASE_URL = 'ws://localhost:8000';

const FileUpload = () => {
    const [files, setFiles] = useState([]); // [{ file, name, size, status, progress, result, error, ws }]
    const [selectedIdx, setSelectedIdx] = useState(null);

    // Handle file selection (drag-and-drop or click)
    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles && acceptedFiles.length > 0) {
            const newFiles = acceptedFiles.map(file => ({
                file,
                name: file.name,
                size: (file.size / 1024).toFixed(2) + ' KB',
                status: '',
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
            'application/pdf': ['.pdf'],
            'application/msword': ['.doc'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
        },
        disabled: false
    });

    // Upload all files that are not yet started
    const handleUploadAll = () => {
        files.forEach((f, idx) => {
            if (!f.status || f.status === 'Stopped' || f.status === 'Failed') uploadFile(f, idx);
        });
    };

    // Upload a single file
    const uploadFile = (fileObj, idx) => {
        const formData = new FormData();
        formData.append('file', fileObj.file);
        updateFile(idx, { status: 'Started', progress: 0, error: null, isProcessing: true });
        connectWebSocket(fileObj.name, idx);
        fetch(UPLOAD_URL, {
            method: 'POST',
            body: formData,
        })
        .then(res => res.json())
        .then(data => {
            updateFile(idx, { result: data, isProcessing: false });
        })
        .catch(err => {
            updateFile(idx, { status: 'Failed', error: err.message, isProcessing: false });
        });
    };

    // Connect to WebSocket for status updates
    const connectWebSocket = (fileName, idx) => {
        const wsConnection = new WebSocket(`${WS_BASE_URL}/ws/status/${fileName}`);
        wsConnection.onopen = () => {
            updateFile(idx, { progress: 10 });
        };
        wsConnection.onmessage = (event) => {
            const status = event.data.split(':')[0].trim();
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
        };
        wsConnection.onclose = () => {
            // Optionally handle close
        };
        wsConnection.onerror = () => {
            updateFile(idx, { status: 'Failed', error: 'WebSocket error', isProcessing: false });
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

    // Cleanup all websockets on unmount
    useEffect(() => {
        return () => {
            files.forEach(f => { if (f.ws) f.ws.close(); });
        };
        // eslint-disable-next-line
    }, []);

    return (
        <div className="file-upload-container">
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
                            <div className="dropzone-formats">Supported formats: PDF, TXT, DOC, DOCX (Max: 10MB)</div>
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
                                    <span className={`status-badge status-${f.status.replace(' ', '-')}`}>{f.status}</span>
                                    <button onClick={() => handleRemove(idx)} className="remove-file-btn">&times;</button>
                                </div>
                            </div>
                            <div className="progress-container">
                                <div className="progress-bar" style={{ width: `${f.progress}%` }}></div>
                            </div>
                            <div className="file-upload-card-actions">
                                <button
                                    onClick={() => uploadFile(f, idx)}
                                    disabled={f.isProcessing || f.status === 'Completed'}
                                    className="upload-button"
                                >
                                    {f.status === 'Completed' ? 'Re-upload' : 'Upload'}
                                </button>
                                {f.isProcessing && (
                                    <button
                                        onClick={() => handleCancel(idx)}
                                        className="cancel-button"
                                    >
                                        Cancel
                                    </button>
                                )}
                                <button
                                    onClick={() => setSelectedIdx(idx)}
                                    disabled={!f.result}
                                    className="upload-button"
                                >
                                    View
                                </button>
                            </div>
                            {f.error && <div className="error-message">Error: {f.error}</div>}
                        </li>
                    ))}
                </ul>
                
                {selectedIdx !== null && files[selectedIdx] && files[selectedIdx].result && (
                    <div className="result-section" style={{ marginTop: 32 }}>
                        <h3>Result for: {files[selectedIdx].name}</h3>
                        <div className="results-content">
                            {typeof files[selectedIdx].result.results === 'string' ? (
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>{files[selectedIdx].result.results}</ReactMarkdown>
                            ) : (
                                <pre>{JSON.stringify(files[selectedIdx].result.results, null, 2)}</pre>
                            )}
                        </div>
                        <button className="upload-button" onClick={() => setSelectedIdx(null)} style={{ marginTop: 12 }}>Close</button>
                    </div>
                )}
            </div>
            <div className="dashboard-card">
                <StatusDashboard files={files} />
            </div>
        </div>
    );
};

export default FileUpload;
