import React, { useState } from 'react';

interface RUPMenuItemProps {
  collapsed?: boolean;
  onUploadComplete?: () => void;
}

const RUPMenuItem: React.FC<RUPMenuItemProps> = ({ collapsed = false, onUploadComplete }) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>({});
  const [dragOver, setDragOver] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload-rup', { method: 'POST', body: formData });
      const data = await response.json();
      setResult(data);
      if (data.success) {
        window.dispatchEvent(new CustomEvent('rup-data-updated'));
        onUploadComplete?.();
        setTimeout(() => { setModalOpen(false); setFile(null); setResult({}); }, 2000);
      }
    } catch (error: any) {
      setResult({ success: false, message: error.message });
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setModalOpen(true)}
        className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 text-gray-300 hover:bg-gray-800 hover:text-white ${collapsed ? 'justify-center' : ''}`}
        title={collapsed ? "Upload Data RUP" : ""}
      >
        <span className="text-xl">📤</span>
        {!collapsed && <span className="text-sm font-medium">Upload RUP</span>}
      </button>

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4">
            <div className="flex justify-between items-center px-6 py-4 border-b">
              <h3 className="text-lg font-semibold">📤 Upload Data RUP</h3>
              <button onClick={() => { setModalOpen(false); setFile(null); setResult({}); }} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <div className="p-6">
              <div className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all ${dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => { e.preventDefault(); setDragOver(false); if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]); }}
                onClick={() => document.getElementById('rup-file-input')?.click()}>
                <div className="text-4xl mb-2">📁</div>
                <div className="text-gray-600">Drag & drop atau klik untuk memilih</div>
                <div className="text-xs text-gray-400 mt-2">CSV, Excel (.xlsx, .xls) | Max 50MB</div>
                <input id="rup-file-input" type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={(e) => e.target.files && setFile(e.target.files[0])} />
              </div>
              {file && <div className="mt-4 p-3 bg-gray-100 rounded-lg text-sm">{file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</div>}
              <button onClick={handleUpload} disabled={!file || uploading} className={`w-full mt-4 px-4 py-2 rounded-lg font-medium ${!file || uploading ? 'bg-gray-300 cursor-not-allowed' : 'bg-green-600 text-white hover:bg-green-700'}`}>
                {uploading ? 'Memproses...' : 'Upload Data'}
              </button>
              {result.message && <div className={`mt-4 p-3 rounded-lg text-sm ${result.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>{result.message}</div>}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default RUPMenuItem;
