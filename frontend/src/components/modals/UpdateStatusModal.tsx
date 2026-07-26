import React, { useState } from 'react';
import { BaseModal } from './BaseModal';
import { CheckCircle, X } from 'lucide-react';

interface UpdateStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (status: string) => void;
  currentStatus: string;
  title: string;
}

const STATUS_OPTIONS = [
  { value: 'PENDING', label: 'Pending', color: 'bg-yellow-500/20 text-yellow-400' },
  { value: 'IN_PROGRESS', label: 'Dalam Proses', color: 'bg-blue-500/20 text-blue-400' },
  { value: 'REVIEW', label: 'Review', color: 'bg-purple-500/20 text-purple-400' },
  { value: 'COMPLETED', label: 'Selesai', color: 'bg-green-500/20 text-green-400' },
  { value: 'ESCALATED', label: 'Ditingkatkan', color: 'bg-red-500/20 text-red-400' },
];

export const UpdateStatusModal: React.FC<UpdateStatusModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  currentStatus,
  title,
}) => {
  const [selectedStatus, setSelectedStatus] = useState(currentStatus);

  return (
    <BaseModal isOpen={isOpen} onClose={onClose} title="📝 Update Status" size="md">
      <div className="space-y-4">
        <p className="text-dark-muted text-sm">
          Ubah status investigasi: <span className="text-white font-medium">{title}</span>
        </p>
        <div className="space-y-2">
          {STATUS_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setSelectedStatus(opt.value)}
              className={`w-full text-left px-4 py-3 rounded-lg border transition-all ${
                selectedStatus === opt.value
                  ? 'border-primary-500 bg-primary-500/10'
                  : 'border-dark-border hover:border-dark-border/80'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${opt.color}`}>
                  {opt.label}
                </span>
                {selectedStatus === opt.value && (
                  <CheckCircle className="w-4 h-4 text-primary-400" />
                )}
              </div>
            </button>
          ))}
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
              if (selectedStatus !== currentStatus) {
                onConfirm(selectedStatus);
              }
              onClose();
            }}
            className="px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors"
          >
            Simpan
          </button>
        </div>
      </div>
    </BaseModal>
  );
};

export default UpdateStatusModal;
