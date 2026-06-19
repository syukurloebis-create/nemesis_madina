// EvidenceUpload.tsx - Upload evidence with custody
import React, { useState, useRef } from 'react';
import { Upload, X, File, Check, AlertTriangle, Loader2, Shield } from 'lucide-react';
import api from '../../services/api';

interface EvidenceUploadProps {
  caseId: string;
  onUploadComplete?: (data: any) => void;
  className?: string;
}

export const EvidenceUpload: React.FC<EvidenceUploadProps> = ({
  caseId,
  onUploadComplete,
  className = ''
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selected = event.target.files?.[0];
    if (selected) {
      if (selected.size > 50 * 1024 * 1024) {
        setError('File size exceeds 50MB limit');
        return;
      }
      setFile(selected);
      setError(null);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setUploadProgress(0);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('case_id', caseId);

    try {
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 300);

      const response = await api.post('/api/v1/evidence/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      clearInterval(progressInterval);
      setUploadProgress(100);
      setResult(response.data);
      
      // Auto-verify after upload
      await handleVerify(response.data.id);
      
      if (onUploadComplete) {
        onUploadComplete(response.data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleVerify = async (evidenceId: string) => {
    setVerifying(true);
    try {
      const response = await api.post(`/api/v1/evidence/${evidenceId}/verify`);
      setResult((prev: any) => ({ ...prev, ...response.data }));
    } catch (err: any) {
      console.error('Verification failed:', err);
    } finally {
      setVerifying(false);
    }
  };

  const handleRemove = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className={`glass-card p-4 ${className}`}>
      <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
        <Shield className="w-4 h-4 text-primary-400" />
        Upload Evidence
      </h3>

      {!file && !result && (
        <div
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-dark-border rounded-lg p-8 text-center cursor-pointer hover:border-primary-500/50 transition-colors"
        >
          <Upload className="w-12 h-12 text-dark-muted mx-auto mb-3" />
          <p className="text-dark-muted">Click or drag to upload</p>
          <p className="text-xs text-dark-muted/60 mt-1">PDF, PNG, JPG, DOC (max 50MB)</p>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileSelect}
            className="hidden"
            accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.xls,.xlsx"
          />
        </div>
      )}

      {file && !result && (
        <div className="bg-dark-bg rounded-lg p-3 border border-dark-border">
          <div className="flex items-center gap-3">
            <File className="w-8 h-8 text-primary-400" />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white truncate">{file.name}</p>
              <p className="text-xs text-dark-muted">{formatFileSize(file.size)}</p>
            </div>
            <button
              onClick={handleRemove}
              className="p-1 text-dark-muted hover:text-red-400 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {uploading && (
            <div className="mt-2">
              <div className="w-full h-1.5 bg-dark-border rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-500 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-xs text-dark-muted mt-1">{uploadProgress}%</p>
            </div>
          )}

          {!uploading && (
            <button
              onClick={handleUpload}
              className="mt-2 w-full py-2 bg-primary-500/20 hover:bg-primary-500/30 rounded-lg text-sm text-primary-400 transition-colors"
            >
              Upload & Verify
            </button>
          )}

          {uploading && (
            <div className="mt-2 flex items-center justify-center gap-2 text-dark-muted">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Uploading...</span>
            </div>
          )}
        </div>
      )}

      {result && (
        <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
          <div className="flex items-center gap-2 text-green-400">
            {verifying ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Check className="w-5 h-5" />
            )}
            <span className="font-medium">
              {verifying ? 'Verifying...' : 'Upload Successful'}
            </span>
          </div>
          <div className="mt-2 text-sm text-dark-muted space-y-1">
            <p>File: {result.filename}</p>
            <p>Trust Score: {result.trust_score}%</p>
            <p>Status: {result.status}</p>
            <p className="text-xs text-dark-muted/60">ID: {result.id}</p>
          </div>
          <button
            onClick={handleRemove}
            className="mt-2 text-sm text-primary-400 hover:text-primary-300"
          >
            Upload Another
          </button>
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
          <div className="flex items-center gap-2 text-red-400">
            <AlertTriangle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default EvidenceUpload;
