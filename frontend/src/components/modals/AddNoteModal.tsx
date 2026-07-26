import React, { useState } from 'react';
import { BaseModal } from './BaseModal';

interface AddNoteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (note: string) => void;
  title: string;
}

export const AddNoteModal: React.FC<AddNoteModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
}) => {
  const [note, setNote] = useState('');

  return (
    <BaseModal isOpen={isOpen} onClose={onClose} title="📝 Tambah Catatan" size="md">
      <div className="space-y-4">
        <p className="text-dark-muted text-sm">
          Tambahkan catatan untuk: <span className="text-white font-medium">{title}</span>
        </p>
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="Tulis catatan di sini..."
          className="w-full h-32 px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-dark-muted focus:outline-none focus:border-primary-500 resize-none"
        />
        <div className="flex justify-end gap-3 pt-4 border-t border-dark-border">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-dark-hover text-dark-muted rounded hover:text-white transition-colors"
          >
            Batal
          </button>
          <button
            onClick={() => {
              if (note.trim()) {
                onConfirm(note);
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

export default AddNoteModal;
