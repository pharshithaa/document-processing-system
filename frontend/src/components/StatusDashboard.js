import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, LinearProgress } from '@mui/material';
import './StatusDashboard.css';

const StatusDashboard = ({ files }) => {
    return (
        <div className="status-dashboard">
            <div className="dashboard-heading">
                Status Dashboard
            </div>

            <TableContainer style={{ borderRadius: 16, overflow: 'hidden' }}>
                <Table aria-label="document status table" size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell style={{ fontWeight: 600, fontSize: '0.9rem', color: '#34495e' }}>Document Name</TableCell>
                            <TableCell style={{ fontWeight: 600, fontSize: '0.9rem', color: '#34495e' }}>Type</TableCell>
                            <TableCell style={{ fontWeight: 600, fontSize: '0.9rem', color: '#34495e' }}>Pages</TableCell>
                            <TableCell style={{ fontWeight: 600, fontSize: '0.9rem', color: '#34495e' }}>Status</TableCell>
                            <TableCell style={{ fontWeight: 600, fontSize: '0.9rem', color: '#34495e' }}>Progress</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {files.map((f, idx) => (
                            <TableRow key={f.name + idx}>
                                <TableCell style={{ fontSize: '0.85rem', color: '#222', fontWeight: 600 }}>{f.name}</TableCell>
                                <TableCell style={{ fontSize: '0.85rem', color: '#6c757d' }}>{f.type || (f.result?.metadata?.is_scanned !== undefined ? (f.result.metadata.is_scanned ? 'Scanned PDF' : 'Digital') : '--')}</TableCell>
                                <TableCell style={{ fontSize: '0.85rem', color: '#6c757d' }}>{f.pages || f.result?.metadata?.pages || '--'}</TableCell>
                                <TableCell style={{ fontSize: '0.85rem' }}>
                                    {f.status === 'Completed' && <span style={{color: '#388e3c', fontWeight: 500}}>✅ Completed</span>}
                                    {f.status === 'Failed' && <span style={{color: '#d32f2f', fontWeight: 500}}>❌ Failed</span>}
                                    {(f.status === 'Processing' || f.status === 'Started' || f.status === 'Uploading' || f.status === 'Extracting' || f.status === 'Extracted') && <span style={{color: '#856404', fontWeight: 500}}>🟡 In-Progress</span>}
                                </TableCell>
                                <TableCell style={{ fontSize: '0.85rem' }}>
                                    {f.status === 'Completed' ? '100%' : f.status === 'Failed' ? '❌' : `${f.progress}%`}
                                    {f.status !== 'Failed' && (
                                        <LinearProgress 
                                            variant="determinate" 
                                            value={f.progress} 
                                            style={{ 
                                                marginTop: 4, 
                                                height: '4px', 
                                                borderRadius: '2px',
                                                backgroundColor: 'rgba(52, 73, 94, 0.1)'
                                            }}
                                            sx={{
                                                '& .MuiLinearProgress-bar': {
                                                    backgroundColor: '#34495e'
                                                }
                                            }}
                                        />
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </div>
    );
};

export default StatusDashboard;
