import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import FileUpload from './components/FileUpload';
import './components/FileUpload.css';

// Create a client
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        <main className="p-8">
          <FileUpload />
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;

