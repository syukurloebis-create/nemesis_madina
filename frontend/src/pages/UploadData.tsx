import React, { useState, useCallback, useRef } from 'react';
import { useAuthStore } from '../stores/authStore';
import * as XLSX from 'xlsx';

interface UploadFile {
  id: string;
  name: string;
  type: string;
  size: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  message?: string;
  data?: any[];
  uploadTime: string;
}

interface ProcessingResult {
  success: boolean;
  total_rows: number;
  processed_rows: number;
  failed_rows: number;
  message: string;
  errors?: Array<{ row: number; error: string }>;
}

const UploadData: React.FC = () => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState<ProcessingResult | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'history' | 'templates'>('upload');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { token } = useAuthStore();

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const readFile = (file: File): Promise<any[]> => {
    return new Promise((resolve, reject) => {
      const extension = file.name.split('.').pop()?.toLowerCase();
      
      if (extension === 'csv' || extension === 'json') {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const content = e.target?.result as string;
            if (extension === 'json') {
              const data = JSON.parse(content);
              resolve(Array.isArray(data) ? data : [data]);
            } else {
              // Parse CSV
              const lines = content.split('\n');
              const headers = lines[0].split(',');
              const rows = lines.slice(1).filter(line => line.trim()).map(line => {
                const values = line.split(',');
                const obj: any = {};
                headers.forEach((header, idx) => {
                  obj[header.trim()] = values[idx]?.trim();
                });
                return obj;
              });
              resolve(rows);
            }
          } catch (error) {
            reject(error);
          }
        };
        reader.onerror = reject;
        reader.readAsText(file);
      } else if (extension === 'xlsx' || extension === 'xls') {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const data = new Uint8Array(e.target?.result as ArrayBuffer);
            const workbook = XLSX.read(data, { type: 'array' });
            const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
            const rows = XLSX.utils.sheet_to_json(firstSheet);
            resolve(rows);
          } catch (error) {
            reject(error);
          }
        };
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
      } else {
        reject(new Error('Unsupported file format'));
      }
    });
  };

  const processData = async (file: UploadFile, data: any[]) => {
    try {
      // Update status to uploading
      setFiles(prev => prev.map(f => 
        f.id === file.id ? { ...f, status: 'uploading', progress: 30 } : f
      ));

      // Send to backend
      const response = await fetch('http://localhost/api/upload/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          filename: file.name,
          file_type: file.type,
          data: data,
          total_rows: data.length
        })
      });

      setFiles(prev => prev.map(f => 
        f.id === file.id ? { ...f, progress: 80 } : f
      ));

      if (response.ok) {
        const result = await response.json();
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { 
            ...f, 
            status: 'success', 
            progress: 100, 
            message: `Successfully processed ${result.processed_rows || data.length} rows`,
            data: data 
          } : f
        ));
        setResults(result);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      setFiles(prev => prev.map(f => 
        f.id === file.id ? { 
          ...f, 
          status: 'error', 
          progress: 0, 
          message: error instanceof Error ? error.message : 'Upload failed' 
        } : f
      ));
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);
    if (selectedFiles.length === 0) return;

    const newFiles: UploadFile[] = selectedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      type: file.type,
      size: file.size,
      status: 'pending',
      progress: 0,
      uploadTime: new Date().toLocaleString()
    }));

    setFiles(prev => [...newFiles, ...prev]);
    setProcessing(true);

    for (const newFile of newFiles) {
      const file = selectedFiles.find(f => f.name === newFile.name);
      if (file) {
        try {
          const data = await readFile(file);
          await processData(newFile, data);
        } catch (error) {
          setFiles(prev => prev.map(f => 
            f.id === newFile.id ? { 
              ...f, 
              status: 'error', 
              message: error instanceof Error ? error.message : 'Failed to read file' 
            } : f
          ));
        }
      }
    }

    setProcessing(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'uploading': return '⏳';
      default: return '⏸';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-400';
      case 'error': return 'text-red-400';
      case 'uploading': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const clearFiles = () => {
    setFiles([]);
    setResults(null);
  };

  const downloadTemplate = (format: string) => {
    const templates: Record<string, any[]> = {
      vendors: [
        { name: 'PT. Contoh Vendor', registration_number: '1234567890', tax_id: '01.234.567.8-901.000', address: 'Jl. Contoh No. 1', city: 'Jakarta', province: 'DKI Jakarta', business_type: 'Kontraktor', risk_score: 50 }
      ],
      cases: [
        { title: 'Contoh Kasus', description: 'Deskripsi kasus', priority: 'HIGH', status: 'OPEN' }
      ],
      evidence: [
        { title: 'Contoh Bukti', description: 'Deskripsi bukti', type: 'document', case_id: 'CASE-001' }
      ]
    };

    const selectedTemplate = templates[format] || templates.vendors;
    const ws = XLSX.utils.json_to_sheet(selectedTemplate);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Template');
    XLSX.writeFile(wb, `template_${format}.xlsx`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <h1 className="text-2xl font-bold text-white">Upload Data</h1>
        <p className="text-gray-400 text-sm mt-1">Upload XLS, CSV, or JSON files to import data into the system</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-700">
        <nav className="flex gap-6">
          {(['upload', 'history', 'templates'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-1 text-sm font-medium transition-colors ${
                activeTab === tab 
                  ? 'text-green-400 border-b-2 border-green-400' 
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              {tab === 'upload' ? '📤 Upload Files' : tab === 'history' ? '📋 Upload History' : '📄 Templates'}
            </button>
          ))}
        </nav>
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          {/* Upload Area */}
          <div 
            className="border-2 border-dashed border-gray-600 rounded-xl p-8 text-center hover:border-green-500 transition-colors cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".xlsx,.xls,.csv,.json"
              onChange={handleFileUpload}
              className="hidden"
            />
            <div className="text-5xl mb-4">📁</div>
            <h3 className="text-lg font-semibold text-white mb-2">Drop files here or click to upload</h3>
            <p className="text-gray-400 text-sm">Supported formats: XLSX, XLS, CSV, JSON</p>
            <div className="flex gap-2 justify-center mt-4">
              <span className="px-2 py-1 bg-gray-700 rounded text-xs">Maximum file size: 50MB</span>
              <span className="px-2 py-1 bg-gray-700 rounded text-xs">Bulk upload supported</span>
            </div>
          </div>

          {/* File List with Scroll */}
          {files.length > 0 && (
            <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-700 flex justify-between items-center">
                <h2 className="text-lg font-semibold text-white">Upload Queue ({files.length})</h2>
                <button onClick={clearFiles} className="text-sm text-red-400 hover:text-red-300">Clear All</button>
              </div>
              <div className="max-h-96 overflow-y-auto divide-y divide-gray-700">
                {files.map((file) => (
                  <div key={file.id} className="p-4 hover:bg-gray-700/30">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className="text-xl">
                          {file.name.endsWith('.xlsx') || file.name.endsWith('.xls') ? '📊' : 
                           file.name.endsWith('.csv') ? '📄' : '📋'}
                        </span>
                        <div>
                          <p className="font-medium text-white">{file.name}</p>
                          <p className="text-xs text-gray-500">{formatFileSize(file.size)} • {file.uploadTime}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className={`text-sm font-semibold ${getStatusColor(file.status)}`}>
                          {getStatusIcon(file.status)} {file.status}
                        </span>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    {file.status === 'uploading' && (
                      <div className="w-full bg-gray-700 rounded-full h-1.5 mt-2">
                        <div className="bg-green-500 h-1.5 rounded-full transition-all duration-300" style={{ width: `${file.progress}%` }}></div>
                      </div>
                    )}
                    
                    {/* Message */}
                    {file.message && (
                      <p className={`text-xs mt-2 ${file.status === 'error' ? 'text-red-400' : 'text-green-400'}`}>
                        {file.message}
                      </p>
                    )}

                    {/* Data Preview */}
                    {file.status === 'success' && file.data && file.data.length > 0 && (
                      <div className="mt-3 text-xs text-gray-500">
                        <details>
                          <summary className="cursor-pointer hover:text-gray-300">Preview data ({file.data.length} rows)</summary>
                          <div className="mt-2 overflow-x-auto">
                            <table className="text-xs">
                              <thead className="text-gray-400">
                                <tr>
                                  {Object.keys(file.data[0] || {}).slice(0, 5).map((key) => (
                                    <th key={key} className="px-2 py-1 text-left">{key}</th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {file.data.slice(0, 3).map((row, idx) => (
                                  <tr key={idx}>
                                    {Object.values(row).slice(0, 5).map((val: any, i) => (
                                      <td key={i} className="px-2 py-1 text-gray-400">{String(val).slice(0, 30)}</td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </details>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Processing Results */}
          {results && results.processed_rows > 0 && (
            <div className={`rounded-xl p-4 border ${
              results.success ? 'bg-green-500/10 border-green-500/30' : 'bg-red-500/10 border-red-500/30'
            }`}>
              <div className="flex items-center gap-3">
                <span className="text-2xl">{results.success ? '✅' : '❌'}</span>
                <div>
                  <h3 className="font-semibold text-white">{results.message}</h3>
                  <p className="text-sm text-gray-400">
                    Total: {results.total_rows} rows • Processed: {results.processed_rows} • Failed: {results.failed_rows}
                  </p>
                </div>
              </div>
              {results.errors && results.errors.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-700">
                  <p className="text-sm text-red-400 mb-2">Errors:</p>
                  <div className="max-h-32 overflow-y-auto text-xs space-y-1">
                    {results.errors.map((err, idx) => (
                      <p key={idx} className="text-gray-400">Row {err.row}: {err.error}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Upload History</h2>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {files.length === 0 ? (
              <div className="p-8 text-center text-gray-500">No upload history yet</div>
            ) : (
              <div className="divide-y divide-gray-700">
                {files.map((file) => (
                  <div key={file.id} className="p-4 hover:bg-gray-700/30">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-white">{file.name}</p>
                        <p className="text-xs text-gray-500">{file.uploadTime}</p>
                      </div>
                      <div className="text-right">
                        <span className={`text-sm ${getStatusColor(file.status)}`}>
                          {getStatusIcon(file.status)} {file.status}
                        </span>
                        {file.data && (
                          <p className="text-xs text-gray-500">{file.data.length} rows imported</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 text-center hover:border-green-500 transition-colors">
            <div className="text-4xl mb-3">🏢</div>
            <h3 className="font-semibold text-white mb-2">Vendor Template</h3>
            <p className="text-xs text-gray-400 mb-4">Template for importing vendor data</p>
            <button onClick={() => downloadTemplate('vendors')} className="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg text-sm hover:bg-green-500/30">
              Download Template
            </button>
          </div>
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 text-center hover:border-green-500 transition-colors">
            <div className="text-4xl mb-3">📋</div>
            <h3 className="font-semibold text-white mb-2">Case Template</h3>
            <p className="text-xs text-gray-400 mb-4">Template for importing case data</p>
            <button onClick={() => downloadTemplate('cases')} className="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg text-sm hover:bg-green-500/30">
              Download Template
            </button>
          </div>
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 text-center hover:border-green-500 transition-colors">
            <div className="text-4xl mb-3">📎</div>
            <h3 className="font-semibold text-white mb-2">Evidence Template</h3>
            <p className="text-xs text-gray-400 mb-4">Template for importing evidence data</p>
            <button onClick={() => downloadTemplate('evidence')} className="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg text-sm hover:bg-green-500/30">
              Download Template
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadData;
