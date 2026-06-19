// src/app/routes/UploadRUP.tsx
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle, X, Download, Eye } from 'lucide-react';
import * as XLSX from 'xlsx';
import toast from 'react-hot-toast';

interface PreviewData {
  headers: string[];
  rows: any[][];
  totalRows: number;
}

const UploadRUP: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = [...uploadedFiles, ...acceptedFiles];
    setUploadedFiles(newFiles);
    acceptedFiles.forEach(file => {
      previewFile(file);
    });
  }, [uploadedFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxSize: 50 * 1024 * 1024 // 50MB
  });

  const previewFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const data = new Uint8Array(e.target?.result as ArrayBuffer);
      const workbook = XLSX.read(data, { type: 'array' });
      const firstSheet = workbook.Sheets[workbook.SheetNames[0]];
      const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 });
      
      const headers = jsonData[0] as string[];
      const rows = jsonData.slice(1, 11) as any[][];
      
      setPreviewData({
        headers,
        rows,
        totalRows: jsonData.length - 1
      });
    };
    reader.readAsArrayBuffer(file);
  };

  const handleUpload = async () => {
    if (uploadedFiles.length === 0) {
      toast.error('Pilih file terlebih dahulu');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    
    try {
      // Simulate upload progress
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setUploadProgress(i);
      }
      
      // TODO: Implement actual upload to backend
      // const formData = new FormData();
      // uploadedFiles.forEach(file => formData.append('files', file));
      // await api.uploadRUP(formData);
      
      await new Promise(resolve => setTimeout(resolve, 500));
      setUploadSuccess(true);
      toast.success(`${uploadedFiles.length} file berhasil diupload`);
      
      // Reset after 3 seconds
      setTimeout(() => {
        setUploadedFiles([]);
        setPreviewData(null);
        setUploadSuccess(false);
      }, 3000);
      
    } catch (error) {
      toast.error('Gagal upload file');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
    if (uploadedFiles.length === 1) {
      setPreviewData(null);
    }
  };

  const downloadTemplate = () => {
    const template = [
      ['ID Paket', 'Nama Paket', 'Pagu', 'Jenis Pengadaan', 'Tahun', 'Instansi', 'Lokasi'],
      ['66770962', 'Rehabilitasi Ruang Kelas SD Negeri 314', '300000000', 'Pekerjaan Konstruksi', '2026', 'DINAS PENDIDIKAN', 'Mandailing Natal'],
      ['66770954', 'Rehabilitasi Ruang Kelas SD Negeri 181', '200000000', 'Pekerjaan Konstruksi', '2026', 'DINAS PENDIDIKAN', 'Mandailing Natal'],
    ];
    
    const ws = XLSX.utils.aoa_to_sheet(template);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Template RUP');
    XLSX.writeFile(wb, 'template_rup.xlsx');
    toast.success('Template downloaded');
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Upload Data RUP</h1>
        <p className="text-sm text-gray-500 mt-1">
          Upload file CSV atau Excel (XLSX, XLS) untuk mengimpor data RUP
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Area */}
        <div className="lg:col-span-2">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-blue-400'
            } ${uploadSuccess ? 'bg-green-50 border-green-500' : ''}`}
          >
            <input {...getInputProps()} />
            {uploadSuccess ? (
              <CheckCircle className="w-12 h-12 mx-auto text-green-500 mb-4" />
            ) : (
              <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            )}
            <p className="text-gray-600">
              {isDragActive
                ? 'Lepaskan file di sini'
                : 'Drag & drop atau klik untuk memilih'}
            </p>
            <p className="text-xs text-gray-400 mt-2">
              CSV, Excel (.xlsx, .xls) | Max 50MB
            </p>
          </div>

          {/* Upload Progress */}
          {uploading && (
            <div className="mt-4">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>Mengupload...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Uploaded Files List */}
          {uploadedFiles.length > 0 && !uploadSuccess && (
            <div className="mt-4 bg-white rounded-lg shadow">
              <div className="px-4 py-3 border-b border-gray-200">
                <h3 className="font-medium text-gray-900">File yang akan diupload</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {uploadedFiles.map((file, idx) => (
                  <div key={idx} className="px-4 py-3 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <FileSpreadsheet className="w-5 h-5 text-green-600" />
                      <span className="text-sm text-gray-700">{file.name}</span>
                      <span className="text-xs text-gray-400">
                        ({(file.size / 1024).toFixed(2)} KB)
                      </span>
                    </div>
                    <button
                      onClick={() => removeFile(idx)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
              <div className="px-4 py-3 bg-gray-50 flex justify-between items-center">
                <button
                  onClick={downloadTemplate}
                  className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                >
                  <Download className="w-4 h-4" />
                  Download Template
                </button>
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {uploading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      Upload Data
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Info Panel */}
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <h3 className="font-medium text-blue-800 mb-2">Format File yang Didukung</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>✓ CSV (comma separated)</li>
            <li>✓ Excel XLSX (Excel 2007+)</li>
            <li>✓ Excel XLS (Excel 97-2003)</li>
          </ul>
          <div className="mt-4 pt-3 border-t border-blue-200">
            <h4 className="font-medium text-blue-800 mb-1">Struktur Data yang Diharapkan</h4>
            <ul className="text-xs text-blue-600 space-y-1">
              <li>• ID Paket</li>
              <li>• Nama Paket</li>
              <li>• Pagu</li>
              <li>• Jenis Pengadaan</li>
              <li>• Tahun Anggaran</li>
              <li>• Instansi</li>
              <li>• Lokasi</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Preview Data */}
      {previewData && !uploadSuccess && (
        <div className="mt-6 bg-white rounded-lg shadow">
          <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
            <div>
              <h3 className="font-medium text-gray-900">Preview Data</h3>
              <p className="text-xs text-gray-500">
                Menampilkan {Math.min(10, previewData.totalRows)} dari {previewData.totalRows} baris
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Eye className="w-4 h-4 text-gray-400" />
              <span className="text-xs text-gray-500">Validasi struktur data</span>
            </div>
          </div>
          <div className="overflow-x-auto p-4">
            <table className="min-w-full text-sm border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b">
                  {previewData.headers.map((header, idx) => (
                    <th key={idx} className="px-3 py-2 text-left text-xs font-medium text-gray-500 border-r">
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewData.rows.map((row, rowIdx) => (
                  <tr key={rowIdx} className="border-b hover:bg-gray-50">
                    {row.map((cell, cellIdx) => (
                      <td key={cellIdx} className="px-3 py-2 text-xs text-gray-600 border-r">
                        {cell !== undefined && cell !== null ? String(cell).substring(0, 50) : '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {previewData.totalRows > 10 && (
            <div className="px-4 py-2 bg-gray-50 text-center text-xs text-gray-500">
              + {previewData.totalRows - 10} baris lainnya
            </div>
          )}
        </div>
      )}

      {/* Success Message */}
      {uploadSuccess && (
        <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4 text-center">
          <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
          <h3 className="font-medium text-green-800">Upload Berhasil!</h3>
          <p className="text-sm text-green-600 mt-1">
            {uploadedFiles.length} file telah berhasil diupload dan diproses
          </p>
        </div>
      )}
    </div>
  );
};

export default UploadRUP;