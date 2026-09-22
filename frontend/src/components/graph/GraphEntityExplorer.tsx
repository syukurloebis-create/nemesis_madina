import React, { useEffect, useMemo, useState } from 'react';
import { AlertCircle, Network, Search } from 'lucide-react';
import graphApi, { KeyActor } from '../../services/api/graph';

export interface GraphEntityExplorerProps {
  caseId: string;
  onNodeSelect?: (nodeId: string) => void;
  selectedNodeId?: string | null;
  limit?: number;
}

// Deterministic comparator (Amendment 2):
//   1. entity_type priority (alphabetical for now)
//   2. degree DESC
//   3. name ASC (case-insensitive)
//   4. business_key ASC (case-insensitive)
function compareActors(a: KeyActor, b: KeyActor): number {
  const entityTypeCompare = a.entity_type.localeCompare(
    b.entity_type,
    undefined,
    { sensitivity: 'base' },
  );

  if (entityTypeCompare !== 0) return entityTypeCompare;

  if (a.degree !== b.degree) {
    return b.degree - a.degree;
  }

  const nameCompare = a.name.localeCompare(
    b.name,
    undefined,
    { sensitivity: 'base' },
  );

  if (nameCompare !== 0) return nameCompare;

  return a.business_key.localeCompare(
    b.business_key,
    undefined,
    { sensitivity: 'base' },
  );
}

export const GraphEntityExplorer: React.FC<GraphEntityExplorerProps> = ({
  caseId,
  onNodeSelect,
  selectedNodeId,
  limit = 25,
}) => {
  const [actors, setActors] = useState<KeyActor[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function loadActors() {
      if (!caseId) {
        setActors([]);
        setError('Case ID tidak tersedia.');
        return;
      }

      setLoading(true);
      setError(null);

      try {
        // graphApi.getKeyActors returns { case_id, actors, count }
        // (already unwrapped from axios response by .then(r => r.data))
        const response = await graphApi.getKeyActors(caseId, limit);

        if (cancelled) return;

        const data = response?.actors ?? [];
        setActors(Array.isArray(data) ? data : []);
      } catch (err) {
        if (cancelled) return;

        setActors([]);
        setError(
          err instanceof Error
            ? err.message
            : 'Gagal memuat key actors dari Graph API.',
        );
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadActors();

    return () => {
      cancelled = true;
    };
  }, [caseId, limit]);

  const sortedActors = useMemo(
    () => [...actors].sort(compareActors),
    [actors],
  );

  const filteredActors = useMemo(() => {
    const query = search.trim().toLocaleLowerCase();

    if (!query) return sortedActors;

    return sortedActors.filter((actor) => {
      return [
        actor.entity_type,
        actor.name,
        actor.business_key,
      ].some((value) =>
        value.toLocaleLowerCase().includes(query),
      );
    });
  }, [search, sortedActors]);

  const handleSelect = (actor: KeyActor) => {
    onNodeSelect?.(actor.business_key);
  };

  return (
    <section className="rounded-xl border border-gray-700/60 bg-dark-card">
      <div className="border-b border-gray-700/60 px-4 py-3">
        <div className="flex items-center gap-2">
          <Network className="h-4 w-4 text-cyan-400" />
          <div>
            <h3 className="text-sm font-semibold text-white">
              Structural Hubs
            </h3>
            <p className="text-xs text-gray-500">
              Key actors ranked by graph degree
            </p>
          </div>
        </div>

        <div className="relative mt-3">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search name, entity type, or business key..."
            className="w-full rounded-lg border border-gray-700 bg-gray-900/60 py-2 pl-9 pr-3 text-sm text-white outline-none placeholder:text-gray-600 focus:border-cyan-500/60"
          />
        </div>
      </div>

      <div className="px-4 py-3">
        {loading && (
          <div className="py-8 text-center text-sm text-gray-500">
            Memuat key actors...
          </div>
        )}

        {!loading && error && (
          <div className="flex items-start gap-2 rounded-lg border border-red-500/20 bg-red-500/5 p-3 text-sm text-red-300">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {!loading && !error && filteredActors.length === 0 && (
          <div className="py-8 text-center">
            <Network className="mx-auto mb-2 h-8 w-8 text-gray-600" />
            <p className="text-sm text-gray-400">
              {search.trim()
                ? 'Tidak ada key actor yang cocok.'
                : 'Tidak ada key actor yang dikembalikan Graph API.'}
            </p>
          </div>
        )}

        {!loading && !error && filteredActors.length > 0 && (
          <div className="space-y-2">
            {filteredActors.map((actor) => {
              const isSelected =
                selectedNodeId === actor.business_key;

              return (
                <button
                  key={actor.business_key}
                  type="button"
                  onClick={() => handleSelect(actor)}
                  className={`w-full rounded-lg border px-3 py-3 text-left transition ${
                    isSelected
                      ? 'border-cyan-500/70 bg-cyan-500/10'
                      : 'border-gray-700/60 bg-gray-900/30 hover:border-gray-600 hover:bg-gray-900/60'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium text-white">
                        {actor.name}
                      </div>

                      <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-gray-500">
                        <span>{actor.entity_type}</span>
                        <span>•</span>
                        <span className="truncate">
                          {actor.business_key}
                        </span>
                      </div>
                    </div>

                    <div className="shrink-0 text-right">
                      <div className="text-lg font-semibold text-white">
                        {actor.degree}
                      </div>
                      <div className="text-[11px] uppercase tracking-wide text-gray-500">
                        degree
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
};

export default GraphEntityExplorer;
