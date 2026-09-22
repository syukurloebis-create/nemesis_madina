import React from 'react';

export type EntityTypeFilter =
  | 'vendor'
  | 'procurement_record'
  | string;

export type RelationshipTypeFilter =
  | 'VENDOR_HAS_PACKAGE'
  | 'COLLUSION'
  | string;

export type LayoutType = 'dagre' | 'circle';

interface GraphControlsProps {
  entityTypes: EntityTypeFilter[];
  relationshipTypes: RelationshipTypeFilter[];
  availableEntityTypes: EntityTypeFilter[];
  availableRelationshipTypes: RelationshipTypeFilter[];
  layout: LayoutType;
  search: string;
  showAll: boolean;
  nodeCount: number;
  totalNodeCount: number;
  onEntityTypesChange: (value: EntityTypeFilter[]) => void;
  onRelationshipTypesChange: (
    value: RelationshipTypeFilter[],
  ) => void;
  onLayoutChange: (value: LayoutType) => void;
  onSearchChange: (value: string) => void;
  onShowAllChange: (value: boolean) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFit: () => void;
  onReset: () => void;
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

function formatRelationshipType(value: string): string {
  switch (value) {
    case 'VENDOR_HAS_PACKAGE':
      return 'Vendor → Package';

    case 'COLLUSION':
      return 'Collusion';

    default:
      return value.replace(/_/g, ' ');
  }
}

const GraphControls: React.FC<GraphControlsProps> = ({
  entityTypes,
  relationshipTypes,
  availableEntityTypes,
  availableRelationshipTypes,
  layout,
  search,
  showAll,
  nodeCount,
  totalNodeCount,
  onEntityTypesChange,
  onRelationshipTypesChange,
  onLayoutChange,
  onSearchChange,
  onShowAllChange,
  onZoomIn,
  onZoomOut,
  onFit,
  onReset,
}) => {
  const toggleEntityType = (value: EntityTypeFilter) => {
    const exists = entityTypes.includes(value);

    if (exists) {
      onEntityTypesChange(
        entityTypes.filter((item) => item !== value),
      );
      return;
    }

    onEntityTypesChange([...entityTypes, value]);
  };

  const toggleRelationshipType = (
    value: RelationshipTypeFilter,
  ) => {
    const exists = relationshipTypes.includes(value);

    if (exists) {
      onRelationshipTypesChange(
        relationshipTypes.filter((item) => item !== value),
      );
      return;
    }

    onRelationshipTypesChange([...relationshipTypes, value]);
  };

  return (
    <div className="absolute inset-x-0 top-0 z-20 border-b border-gray-800 bg-gray-950/95 backdrop-blur p-3">
      <div className="flex flex-wrap items-center gap-2">
        <div className="text-xs font-semibold uppercase tracking-wide text-gray-500 mr-1">
          Graph
        </div>

        {availableEntityTypes.map((type) => (
          <button
            key={`entity-${type}`}
            type="button"
            onClick={() => toggleEntityType(type)}
            className={[
              'px-3 py-1.5 rounded-lg border text-xs transition',
              entityTypes.includes(type)
                ? 'bg-white/10 border-gray-500 text-white'
                : 'bg-transparent border-gray-800 text-gray-500',
            ].join(' ')}
          >
            {formatEntityType(type)}
          </button>
        ))}

        <span className="mx-1 h-5 w-px bg-gray-800" />

        {availableRelationshipTypes.map((type) => (
          <button
            key={`relationship-${type}`}
            type="button"
            onClick={() => toggleRelationshipType(type)}
            className={[
              'px-3 py-1.5 rounded-lg border text-xs transition',
              relationshipTypes.includes(type)
                ? 'bg-white/10 border-gray-500 text-white'
                : 'bg-transparent border-gray-800 text-gray-500',
            ].join(' ')}
          >
            {formatRelationshipType(type)}
          </button>
        ))}

        <div className="flex-1 min-w-[220px]" />

        <input
          type="search"
          value={search}
          onChange={(event) =>
            onSearchChange(event.target.value)
          }
          placeholder="Cari node…"
          className="w-48 px-3 py-1.5 rounded-lg border border-gray-700 bg-gray-900 text-white text-sm placeholder-gray-600 outline-none focus:border-gray-500"
          aria-label="Cari node graph"
        />

        <select
          value={layout}
          onChange={(event) =>
            onLayoutChange(event.target.value as LayoutType)
          }
          className="px-3 py-1.5 rounded-lg border border-gray-700 bg-gray-900 text-white text-sm outline-none"
          aria-label="Layout graph"
        >
          <option value="dagre">Dagre</option>
          <option value="circle">Circle</option>
        </select>

        <label className="inline-flex items-center gap-2 px-2 text-xs text-gray-400">
          <input
            type="checkbox"
            checked={showAll}
            onChange={(event) =>
              onShowAllChange(event.target.checked)
            }
            className="rounded border-gray-700 bg-gray-900"
          />
          Show all
        </label>

        <span className="text-xs text-gray-500 whitespace-nowrap">
          {nodeCount}/{totalNodeCount}
        </span>

        <button
          type="button"
          onClick={onZoomOut}
          className="px-2.5 py-1.5 rounded-lg border border-gray-700 bg-gray-900 text-gray-300 hover:text-white"
          title="Zoom out"
          aria-label="Zoom out"
        >
          −
        </button>

        <button
          type="button"
          onClick={onZoomIn}
          className="px-2.5 py-1.5 rounded-lg border border-gray-700 bg-gray-900 text-gray-300 hover:text-white"
          title="Zoom in"
          aria-label="Zoom in"
        >
          +
        </button>

        <button
          type="button"
          onClick={onFit}
          className="px-3 py-1.5 rounded-lg border border-gray-700 bg-gray-900 text-gray-300 hover:text-white text-xs"
        >
          Fit
        </button>

        <button
          type="button"
          onClick={onReset}
          className="px-3 py-1.5 rounded-lg border border-gray-700 bg-gray-900 text-gray-300 hover:text-white text-xs"
        >
          Reset
        </button>
      </div>
    </div>
  );
};

export default GraphControls;
