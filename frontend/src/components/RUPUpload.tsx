// src/components/RUPUpload.tsx
import React, { useState } from 'react';
import { api } from '../services/api';

// Tambahkan method upload ke api service jika belum ada
// Atau gunakan fetch langsung

const RUPUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{
    success?: boolean;
    message?: string;
    total?: number;
    new?: number;
    duplicate?: number;
  }>({});
  const [dragOver, setDragOver] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult({});
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setResult({});
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Pilih file terlebih dahulu!');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Gunakan fetch langsung atau tambahkan ke api service
      const response = await fetch('/api/upload-rup', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      setResult(data);
      
      if (data.success) {
        // Trigger event untuk refresh data RUP
        window.dispatchEvent(new CustomEvent('rup-data-updated'));
        // Reset file setelah upload berhasil
        setFile(null);
      }
    } catch (error: any) {
      setResult({
        success: false,
        message: error.message || 'Upload gagal',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow mb-8">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">
          📤 Upload Data RUP (CSV/Excel)
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          Upload file data RUP Mandailing Natal untuk disimpan ke database
        </p>
      </div>
      
      <div className="p-6">
        {/* Drop Zone */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-all duration-200
            ${dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          `}
          onClick={() => document.getElementById('rup-file-input')?.click()}
        >
          <div className="text-4xl mb-2">📁</div>
          <div className="text-gray-600">Drag & drop file atau klik untuk memilih</div>
          <div className="text-xs text-gray-400 mt-2">
            Support: CSV, Excel (.xlsx, .xls) | Max: 50MB
          </div>
          <input
            id="rup-file-input"
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
            className="hidden"
          />
        </div>
        
        {/* File Info */}
        {file && (
          <div className="mt-4 p-3 bg-gray-100 rounded-lg flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-xl">📄</span>
              <span className="text-sm text-gray-700">{file.name}</span>
              <span className="text-xs text-gray-500">
                ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </span>
            </div>
            <button
              onClick={() => setFile(null)}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
        )}
        
        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className={`
            w-full mt-4 px-4 py-2 rounded-lg font-medium
            transition-colors duration-200
            ${!file || uploading
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-green-600 text-white hover:bg-green-700'
            }
          `}
        >
          {uploading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Memproses...
            </span>
          ) : (
            'Upload Data'
          )}
        </button>
        
        {/* Result Message */}
        {result.message && (
          <div className={`
            mt-4 p-3 rounded-lg text-sm
            ${result.success 
              ? 'bg-green-50 text-green-800 border border-green-200' 
              : 'bg-red-50 text-red-800 border border-red-200'
            }
          `}>
            <div className="font-medium mb-1">
              {result.success ? '✓ Berhasil!' : '✗ Gagal!'}
            </div>
            <div>{result.message}</div>
            {result.total !== undefined && (
              <div className="mt-2 text-xs">
                Total: {result.total} | Baru: {result.new} | Duplikat: {result.duplicate}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default RUPUpload;