import React from 'react';
import './StatusDashboard.css';

const StatusDashboard = ({ files }) => {
    return (
        <div className="status-dashboard">
            <h2 className="dashboard-heading">Status Dashboard</h2>
            <div className="doc-list-table-wrapper">
                <table className="doc-list-table">
                    <thead>
                        <tr>
                            <th>Document Name</th>
                            <th>Type</th>
                            <th>Pages</th>
                            <th>Status</th>
                            <th>Progress</th>
                        </tr>
                    </thead>
                    <tbody>
                        {files.map((f, idx) => (
                            <tr key={f.name + idx}>
                                <td>{f.name}</td>
                                <td>{f.type || (f.result?.metadata?.is_scanned !== undefined ? (f.result.metadata.is_scanned ? 'Scanned PDF' : 'Digital') : '--')}</td>
                                <td>{f.pages || f.result?.metadata?.pages || '--'}</td>
                                <td>
                                    {f.status === 'Completed' && <span style={{color: '#388e3c'}}>✅ Completed</span>}
                                    {f.status === 'Failed' && <span style={{color: '#d32f2f'}}>❌ Failed</span>}
                                    {(f.status === 'Processing' || f.status === 'Started' || f.status === 'Uploading' || f.status === 'Extracting' || f.status === 'Extracted') && <span style={{color: '#fbc02d'}}>🟡 In-Progress</span>}
                                </td>
                                <td>
                                    {f.status === 'Completed' ? '100%' : f.status === 'Failed' ? '❌' : `${f.progress}%`}
                                    {f.status !== 'Failed' && (
                                        <div className="progress-container" style={{marginTop: 4}}>
                                            <div className="progress-bar" style={{ width: `${f.progress}%` }}></div>
                                        </div>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default StatusDashboard;
