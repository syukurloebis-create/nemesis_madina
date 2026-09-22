import React from 'react';

import type { GraphNodeDTO } from '../../services/api/graph';

interface EntityDetailsProps {
  entity: GraphNodeDTO;
  degree?: number;
  onClose: () => void;
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return '—';
  }

  if (typeof value === 'string') {
    return value;
  }

  if (
    typeof value === 'number' ||
    typeof value === 'boolean'
  ) {
    return String(value);
  }

  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function formatEntityType(value: string): string {
  switch (value) {
    case 'vendor':
      return 'Vendor';

    case 'procurement_record':
      return 'Procurement Record';

    default:
      return value.replace(/_/g, ' ');
  }
}

const EntityDetails: React.FC<EntityDetailsProps> = ({
  entity,
  degree = 0,
  onClose,
}) => {
  const sourceData =
    entity.extra_data &&
    typeof entity.extra_data === 'object' &&
    'source' in entity.extra_data
      ? (
          entity.extra_data as {
            source?: unknown;
          }
        ).source
      : undefined;

  return (
    <aside className="absolute top-0 right-0 z-30 h-full w-full max-w-[420px] border-l border-gray-700 bg-gray-950/98 shadow-2xl overflow-y-auto">
      <div className="sticky top-0 z-10 flex items-center justify-between border-b border-gray-800 bg-gray-950 px-5 py-4">
        <div>
          <div className="text-xs uppercase tracking-wide text-gray-500">
            Entity Details
          </div>

          <div className="mt-1 text-lg font-semibold text-white">
            {entity.name}
          </div>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="rounded-lg px-3 py-2 text-gray-500 hover:text-white hover:bg-gray-800"
          aria-label="Tutup detail entity"
        >
          ✕
        </button>
      </div>

      <div className="p-5 space-y-5">
        <section>
          <div className="text-xs uppercase tracking-wide text-gray-500 mb-2">
            Identity
          </div>

          <div className="space-y-3">
            <DetailRow
              label="Name"
              value={entity.name}
            />

            <DetailRow
              label="Entity type"
              value={formatEntityType(entity.entity_type)}
            />

            <DetailRow
              label="Business key"
              value={entity.business_key}
            />

            <DetailRow
              label="Source ID"
              value={formatValue(entity.source_id)}
            />

            <DetailRow
              label="Structural degree"
              value={String(degree)}
            />
          </div>
        </section>

        <section>
          <div className="text-xs uppercase tracking-wide text-gray-500 mb-2">
            Source Data
          </div>

          <pre className="rounded-xl border border-gray-800 bg-gray-900 p-4 text-xs text-gray-300 overflow-x-auto whitespace-pre-wrap break-words">
            {formatValue(sourceData ?? entity.extra_data)}
          </pre>
        </section>
      </div>
    </aside>
  );
};

function DetailRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900/60 p-3">
      <div className="text-[11px] uppercase tracking-wide text-gray-600">
        {label}
      </div>
      <div className="mt-1 text-sm text-white break-words">
        {value}
      </div>
    </div>
  );
}

export default EntityDetails;
