// InvestigationWorkspace.tsx
// Investigation Workspace — Case Scoped
// src/components/investigation/InvestigationWorkspace.tsx

import React, { useCallback, useEffect, useState } from 'react';
import { investigationService } from '../../services/investigations';

interface Investigation {
  id: string;
  case_id: string;
  title: string;
  status: string;
  priority: string;
  assigned_to?: string;
  created_at: string;
  updated_at: string;
}

interface InvestigationStats {
  total: number;
  active: number;
  completed: number;
  pending: number;
}

export interface InvestigationWorkspaceProps {
  caseId?: string;
}

export default function InvestigationWorkspace({
  caseId,
}: InvestigationWorkspaceProps) {
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [stats, setStats] = useState<InvestigationStats>({
    total: 0,
    active: 0,
    completed: 0,
    pending: 0,
  });

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!caseId) {
      setInvestigations([]);
      setStats({
        total: 0,
        active: 0,
        completed: 0,
        pending: 0,
      });
      setError(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const [investigationsRes, statsRes] = await Promise.all([
        investigationService.getByCase(caseId),
        investigationService.getStats(caseId),
      ]);

      const investigationsData =
        investigationsRes?.data ?? investigationsRes ?? [];

      const statsData =
        statsRes?.data ?? statsRes ?? {};

      setInvestigations(
        Array.isArray(investigationsData)
          ? investigationsData
          : [],
      );

      setStats({
        total: Number(statsData?.total ?? 0),
        active: Number(statsData?.active ?? 0),
        completed: Number(statsData?.completed ?? 0),
        pending: Number(statsData?.pending ?? 0),
      });
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'Failed to load investigations';

      setError(message);

      console.error(
        'Failed to load investigations:',
        err,
      );
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const handleUpdateStatus = async (
    id: string,
    status: string,
  ) => {
    try {
      await investigationService.updateStatus(
        id,
        status,
      );

      await loadData();
    } catch (err) {
      console.error(
        'Failed to update investigation status:',
        err,
      );

      setError(
        err instanceof Error
          ? err.message
          : 'Failed to update investigation status',
      );
    }
  };

  if (!caseId) {
    return (
      <section className="space-y-6">
        <div className="bg-dark-card border border-dark-border rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white">
            Investigation
          </h2>

          <p className="mt-2 text-sm text-gray-400">
            No case selected.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <div className="bg-dark-card border border-dark-border rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">
              Investigation Workspace
            </h2>

            <p className="mt-1 text-sm text-gray-400">
              Case: {caseId}
            </p>
          </div>

          {loading && (
            <span className="text-sm text-gray-400">
              Loading...
            </span>
          )}
        </div>

        {error && (
          <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 p-4">
            <p className="text-sm text-red-300">
              {error}
            </p>
          </div>
        )}

        {!loading && !error && (
          <>
            <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
              <div className="rounded-lg border border-dark-border p-4">
                <p className="text-xs text-gray-400">
                  Total
                </p>
                <p className="mt-1 text-2xl font-semibold text-white">
                  {stats.total}
                </p>
              </div>

              <div className="rounded-lg border border-dark-border p-4">
                <p className="text-xs text-gray-400">
                  Active
                </p>
                <p className="mt-1 text-2xl font-semibold text-white">
                  {stats.active}
                </p>
              </div>

              <div className="rounded-lg border border-dark-border p-4">
                <p className="text-xs text-gray-400">
                  Completed
                </p>
                <p className="mt-1 text-2xl font-semibold text-white">
                  {stats.completed}
                </p>
              </div>

              <div className="rounded-lg border border-dark-border p-4">
                <p className="text-xs text-gray-400">
                  Pending
                </p>
                <p className="mt-1 text-2xl font-semibold text-white">
                  {stats.pending}
                </p>
              </div>
            </div>

            <div className="mt-6">
              {investigations.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-sm text-gray-300">
                    No investigations have been created for this case.
                  </p>

                  <button
                    type="button"
                    disabled
                    title="Not yet available in this environment"
                    className="mt-4 px-4 py-2 rounded-lg bg-gray-800 text-gray-500 cursor-not-allowed text-sm"
                  >
                    Create Investigation
                  </button>

                  <p className="mt-2 text-xs text-gray-600">
                    Investigation creation is not yet available in this environment.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {investigations.map(
                    (investigation) => (
                      <div
                        key={investigation.id}
                        className="rounded-lg border border-dark-border p-4"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <h3 className="font-medium text-white">
                              {investigation.title}
                            </h3>

                            <p className="mt-1 text-xs text-gray-400">
                              {investigation.priority}
                            </p>
                          </div>

                          <span className="rounded-md bg-gray-800 px-2 py-1 text-xs text-gray-300">
                            {investigation.status}
                          </span>
                        </div>

                        <div className="mt-4 flex gap-2">
                          {investigation.status !==
                            'COMPLETED' && (
                            <button
                              type="button"
                              onClick={() =>
                                void handleUpdateStatus(
                                  investigation.id,
                                  'COMPLETED',
                                )
                              }
                              className="rounded-lg bg-primary-600 px-3 py-2 text-xs text-white hover:bg-primary-500"
                            >
                              Mark completed
                            </button>
                          )}
                        </div>
                      </div>
                    ),
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </section>
  );
}