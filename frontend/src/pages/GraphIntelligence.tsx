import React, { useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  useGraphSummary,
  useGraphMetrics,
  useGraphKeyActors,
  useGraphFull,
} from '../hooks/useGraphQueries';

const GraphIntelligence: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();

  const [fullGraphEnabled, setFullGraphEnabled] = useState(false);

  // ============================================================
  // INITIAL QUERIES
  // Summary + metrics + key actors only.
  // Full graph is intentionally excluded from initial load.
  // ============================================================

  const summaryQuery = useGraphSummary(caseId);
  const metricsQuery = useGraphMetrics(caseId);
  const actorsQuery = useGraphKeyActors(caseId, 20);

  // ============================================================
  // ON-DEMAND FULL GRAPH
  // ============================================================

  const fullGraphQuery = useGraphFull(caseId, fullGraphEnabled);

  // ============================================================
  // DERIVED STATE
  // ============================================================

  if (!caseId) {
    return (
      <div style={{ padding: 24 }}>
        <h2>Graph Intelligence</h2>
        <p>No case selected.</p>
      </div>
    );
  }

  const isInitialLoading =
    summaryQuery.isPending ||
    metricsQuery.isPending ||
    actorsQuery.isPending;

  const initialError =
    summaryQuery.error?.message ||
    metricsQuery.error?.message ||
    actorsQuery.error?.message ||
    null;

  const isInitialError =
    summaryQuery.isError ||
    metricsQuery.isError ||
    actorsQuery.isError;

  const summary = summaryQuery.data;
  const metrics = metricsQuery.data;
  const actors = actorsQuery.data?.actors ?? [];

  const entityBars = useMemo(() => {
    if (!summary) return [];

    return Object.entries(summary.entity_types).sort(
      (a, b) => b[1] - a[1],
    );
  }, [summary]);

  const relBars = useMemo(() => {
    if (!summary) return [];

    return Object.entries(summary.relationship_types).sort(
      (a, b) => b[1] - a[1],
    );
  }, [summary]);

  // ============================================================
  // LOADING
  // ============================================================

  if (isInitialLoading) {
    return (
      <div style={{ padding: 24 }}>
        <h2>Graph Intelligence</h2>
        <p>Loading graph intelligence…</p>
      </div>
    );
  }

  // ============================================================
  // ERROR
  // ============================================================

  if (isInitialError) {
    return (
      <div style={{ padding: 24 }}>
        <h2>Graph Intelligence</h2>
        <div
          style={{
            marginTop: 16,
            padding: 16,
            border: '1px solid #ef4444',
            borderRadius: 8,
            color: '#b91c1c',
          }}
        >
          <strong>Unable to load graph intelligence.</strong>
          <div style={{ marginTop: 8 }}>
            {initialError ?? 'Unknown graph API error.'}
          </div>
        </div>
      </div>
    );
  }

  // ============================================================
  // NO DATA / EMPTY
  // ============================================================

  if (
    !summary ||
    summary.total_entities === 0 ||
    summary.total_relationships === 0
  ) {
    return (
      <div style={{ padding: 24 }}>
        <h2>Graph Intelligence</h2>

        <div
          style={{
            marginTop: 16,
            padding: 20,
            border: '1px solid #ddd',
            borderRadius: 8,
          }}
        >
          <strong>No graph data.</strong>
          <p style={{ marginBottom: 0, color: '#666' }}>
            Case ini belum memiliki graph yang dapat dianalisis.
          </p>
        </div>
      </div>
    );
  }

  // ============================================================
  // SUCCESS
  // ============================================================

  return (
    <div style={{ padding: 24 }}>
      <h2>Graph Intelligence</h2>

      <p style={{ color: '#666' }}>
        Case: {caseId}
      </p>

      {/* ========================================================
          KPI
          ======================================================== */}

      <div
        style={{
          display: 'flex',
          gap: 16,
          margin: '16px 0',
          flexWrap: 'wrap',
        }}
      >
        <KPI
          label="Nodes"
          value={summary.total_entities}
        />

        <KPI
          label="Edges"
          value={summary.total_relationships}
        />

        <KPI
          label="Entity Types"
          value={entityBars.length}
        />

        <KPI
          label="Relationship Types"
          value={relBars.length}
        />

        <KPI
          label="Density"
          value={metrics?.density ?? 0}
          precision={6}
        />
      </div>

      {/* ========================================================
          DISTRIBUTION
          ======================================================== */}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 24,
        }}
      >
        <Panel title="Entity Distribution">
          {entityBars.map(([key, value]) => (
            <Bar
              key={key}
              label={key}
              value={value}
              max={summary.total_entities}
            />
          ))}
        </Panel>

        <Panel title="Relationship Distribution">
          {relBars.map(([key, value]) => (
            <Bar
              key={key}
              label={key}
              value={value}
              max={summary.total_relationships}
            />
          ))}
        </Panel>
      </div>

      {/* ========================================================
          KEY ACTORS
          ======================================================== */}

      <Panel
        title={`Key Actors — top ${actors.length} — ranked by degree`}
      >
        {actors.length === 0 ? (
          <p style={{ color: '#666' }}>
            No key actors returned by Graph API.
          </p>
        ) : (
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
            }}
          >
            <thead>
              <tr
                style={{
                  textAlign: 'left',
                  borderBottom: '1px solid #ddd',
                }}
              >
                <th style={{ padding: '10px 8px' }}>
                  Name
                </th>

                <th style={{ padding: '10px 8px' }}>
                  Type
                </th>

                <th style={{ padding: '10px 8px' }}>
                  Degree
                </th>
              </tr>
            </thead>

            <tbody>
              {actors.map((actor) => (
                <tr
                  key={actor.business_key}
                  style={{
                    borderBottom: '1px solid #f0f0f0',
                  }}
                >
                  <td style={{ padding: '10px 8px' }}>
                    {actor.name}
                  </td>

                  <td style={{ padding: '10px 8px' }}>
                    {actor.entity_type}
                  </td>

                  <td style={{ padding: '10px 8px' }}>
                    {actor.degree}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Panel>

      {/* ========================================================
          FULL GRAPH — ON DEMAND
          ======================================================== */}

      <Panel title="Full Graph">
        <p style={{ color: '#666', marginTop: 0 }}>
          Full graph tidak dimuat pada initial page load.
          Muat hanya saat diperlukan untuk eksplorasi jaringan.
        </p>

        {!fullGraphEnabled && (
          <button
            type="button"
            onClick={() => setFullGraphEnabled(true)}
            style={{
              border: '1px solid #2563eb',
              background: '#2563eb',
              color: '#fff',
              borderRadius: 8,
              padding: '10px 16px',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            Load Full Graph
          </button>
        )}

        {fullGraphEnabled && fullGraphQuery.isPending && (
          <div style={{ marginTop: 12 }}>
            Loading full graph…
          </div>
        )}

        {fullGraphEnabled && fullGraphQuery.isError && (
          <div
            style={{
              marginTop: 12,
              padding: 12,
              border: '1px solid #ef4444',
              borderRadius: 8,
              color: '#b91c1c',
            }}
          >
            {fullGraphQuery.error?.message ||
              'Failed to load full graph.'}
          </div>
        )}

        {fullGraphEnabled &&
          fullGraphQuery.isSuccess &&
          fullGraphQuery.data && (
            <div
              style={{
                marginTop: 16,
                padding: 16,
                border: '1px solid #ddd',
                borderRadius: 8,
              }}
            >
              <strong>Full graph loaded.</strong>

              <div style={{ marginTop: 12 }}>
                Nodes:{' '}
                {fullGraphQuery.data.nodes.length.toLocaleString()}
              </div>

              <div>
                Edges:{' '}
                {fullGraphQuery.data.edges.length.toLocaleString()}
              </div>

              <div>
                Has data:{' '}
                {fullGraphQuery.data.has_data ? 'YES' : 'NO'}
              </div>

              {fullGraphQuery.data.version != null && (
                <div>
                  Version: {fullGraphQuery.data.version}
                </div>
              )}

              {fullGraphQuery.data.checksum && (
                <div
                  style={{
                    marginTop: 8,
                    fontSize: 12,
                    color: '#666',
                    wordBreak: 'break-all',
                  }}
                >
                  Checksum: {fullGraphQuery.data.checksum}
                </div>
              )}

              <p
                style={{
                  marginBottom: 0,
                  marginTop: 12,
                  fontSize: 12,
                  color: '#777',
                }}
              >
                Visualisasi jaringan penuh akan menjadi tahap
                berikutnya; FE-4C hanya memastikan loading
                dilakukan secara on-demand.
              </p>
            </div>
          )}
      </Panel>

      {/* ========================================================
          CONTRACT FOOTER
          ======================================================== */}

      <p
        style={{
          marginTop: 24,
          fontSize: 12,
          color: '#999',
        }}
      >
        Source: /api/v1/graph/cases/{caseId} · Contract F3.3 v1
        (LOCKED) · Actor ranking is structural (degree) ·
        Risk semantics belong to Risk Engine v3.
      </p>
    </div>
  );
};

const KPI: React.FC<{
  label: string;
  value: number;
  precision?: number;
}> = ({
  label,
  value,
  precision,
}) => (
  <div
    style={{
      border: '1px solid #ddd',
      borderRadius: 8,
      padding: 16,
      minWidth: 140,
    }}
  >
    <div
      style={{
        fontSize: 12,
        color: '#666',
      }}
    >
      {label}
    </div>

    <div
      style={{
        fontSize: 24,
        fontWeight: 600,
        marginTop: 4,
      }}
    >
      {precision !== undefined
        ? value.toFixed(precision)
        : value.toLocaleString()}
    </div>
  </div>
);

const Panel: React.FC<{
  title: string;
  children: React.ReactNode;
}> = ({
  title,
  children,
}) => (
  <div
    style={{
      border: '1px solid #ddd',
      borderRadius: 8,
      padding: 16,
      marginTop: 16,
    }}
  >
    <h3 style={{ marginTop: 0 }}>
      {title}
    </h3>

    {children}
  </div>
);

const Bar: React.FC<{
  label: string;
  value: number;
  max: number;
}> = ({
  label,
  value,
  max,
}) => {
  const pct =
    max > 0
      ? Math.round((value / max) * 100)
      : 0;

  return (
    <div style={{ marginBottom: 10 }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: 12,
        }}
      >
        <span>{label}</span>
        <span>
          {value.toLocaleString()} ({pct}%)
        </span>
      </div>

      <div
        style={{
          background: '#eee',
          height: 8,
          borderRadius: 4,
          overflow: 'hidden',
          marginTop: 4,
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            background: '#3b82f6',
            height: '100%',
            borderRadius: 4,
          }}
        />
      </div>
    </div>
  );
};

export default GraphIntelligence;
