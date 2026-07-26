import React, { useState } from 'react';
import { BaseModal } from './BaseModal';
import { AlertTriangle } from 'lucide-react';

interface EscalateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (reason: string) => void;
  title: string;
}

export const EscalateModal: React.FC<EscalateModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
}) => {
  const [reason, setReason] = useState('');
  const [severity, setSeverity] = useState('HIGH');

  return (
    <BaseModal isOpen={isOpen} onClose={onClose} title="⬆️ Eskalasi Investigasi" size="md">
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-yellow-400">
          <AlertTriangle className="w-5 h-5" />
          <span className="text-sm font-medium">Eskalasi: {title}</span>
        </div>
        <div>
          <label className="text-sm text-dark-muted block mb-1">Tingkat Eskalasi</label>
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:border-primary-500"
          >
            <option value="HIGH">Tinggi</option>
            <option value="URGENT">Urgent</option>
            <option value="CRITICAL">Kritis</option>
          </select>
        </div>
        <div>
          <label className="text-sm text-dark-muted block mb-1">Alasan Eskalasi</label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Jelaskan alasan eskalasi..."
            className="w-full h-24 px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-dark-muted focus:outline-none focus:border-primary-500 resize-none"
          />
        </div>
        <div className="flex justify-end gap-3 pt-4 border-t border-dark-border">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-dark-hover text-dark-muted rounded hover:text-white transition-colors"
          >
            Batal
          </button>
          <button
            onClick={() => {
              if (reason.trim()) {
                onConfirm(reason);
              }
              onClose();
            }}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
          >
            Eskalasi
          </button>
        </div>
      </div>
    </BaseModal>
  );
};

export default EscalateModal;
