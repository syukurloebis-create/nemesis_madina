import type cytoscape from 'cytoscape';

const cytoscapeStyles: cytoscape.StylesheetStyle[] = [
  {
    selector: 'node',
    style: {
      'background-color': '#475569',
      label: 'data(name)',
      color: '#f8fafc',
      'font-size': '10px',
      'text-valign': 'bottom',
      'text-halign': 'center',
      'text-margin-y': 7,
      width: 24,
      height: 24,
      'border-width': 1,
      'border-color': '#64748b',
      'overlay-opacity': 0,
      'min-zoomed-font-size': 8,
    },
  },

  {
    selector: 'node[entity_type = "vendor"]',
    style: {
      'background-color': '#2563eb',
      'border-color': '#60a5fa',
      shape: 'round-rectangle',
      width: 30,
      height: 30,
    },
  },

  {
    selector: 'node[entity_type = "procurement_record"]',
    style: {
      'background-color': '#475569',
      'border-color': '#94a3b8',
      shape: 'ellipse',
      width: 20,
      height: 20,
    },
  },

  {
    selector: 'edge',
    style: {
      width: 1,
      'line-color': '#64748b',
      'target-arrow-color': '#64748b',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'arrow-scale': 0.7,
      opacity: 0.65,
    },
  },

  {
    selector: 'edge[relationship_type = "VENDOR_HAS_PACKAGE"]',
    style: {
      'line-color': '#64748b',
      'target-arrow-color': '#64748b',
    },
  },

  {
    selector: 'edge[relationship_type = "COLLUSION"]',
    style: {
      width: 2.5,
      'line-color': '#dc2626',
      'target-arrow-color': '#dc2626',
      opacity: 0.95,
    },
  },

  {
    selector: 'node:selected',
    style: {
      'border-width': 4,
      'border-color': '#f8fafc',
      'overlay-color': '#ffffff',
      'overlay-opacity': 0.12,
      'overlay-padding': 6,
    },
  },

  {
    selector: 'node.search-match',
    style: {
      'border-width': 4,
      'border-color': '#facc15',
      'overlay-color': '#facc15',
      'overlay-opacity': 0.12,
      'overlay-padding': 7,
    },
  },

  {
    selector: 'node:selected.search-match',
    style: {
      'border-width': 5,
      'border-color': '#ffffff',
      'overlay-color': '#facc15',
      'overlay-opacity': 0.16,
      'overlay-padding': 8,
    },
  },

  {
    selector: 'node:active',
    style: {
      'overlay-opacity': 0.08,
    },
  },
];

export default cytoscapeStyles;
