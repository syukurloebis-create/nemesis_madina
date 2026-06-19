import React, { useEffect, useState } from 'react';
import { getGraphCollusion, getGraphStats } from '../services/api';

interface Node {
  id: string;
  name: string;
  risk_score: number;
  type: string;
}

interface Edge {
  source: string;
  target: string;
  type: string;
  confidence: number;
}

export default function CollusionGraph() {
  const [graphData, setGraphData] = useState<{ nodes: Node[]; edges: Edge[] }>({ nodes: [], edges: [] });
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, collusionRes] = await Promise.all([
        getGraphStats().catch(() => ({ data: null })),
        getGraphCollusion().catch(() => ({ data: null }))
      ]);
      
      setStats(statsRes.data);
      
      if (collusionRes.data && collusionRes.data.nodes) {
        setGraphData({
          nodes: collusionRes.data.nodes,
          edges: collusionRes.data.edges || []
        });
        console.log('Graph loaded:', collusionRes.data.nodes.length, 'nodes,', collusionRes.data.edges.length, 'edges');
      } else {
        setGraphData({ nodes: [], edges: [] });
      }
    } catch (err: any) {
      console.error('Gagal memuat data graph:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 70) return 'text-red-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getEdgeBadge = (type: string) => {
    if (type === 'collusion') return 'bg-red-900/50 text-red-400 border border-red-500';
    if (type === 'financial') return 'bg-yellow-900/50 text-yellow-400 border border-yellow-500';
    return 'bg-blue-900/50 text-blue-400 border border-blue-500';
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="text-center py-8 text-gray-400">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400 mx-auto mb-4"></div>
          Memuat data graph...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="text-center py-8">
          <p className="text-red-400">⚠️ Gagal memuat data graph</p>
          <p className="text-gray-500 text-sm mt-2">{error}</p>
          <button onClick={loadData} className="mt-4 px-4 py-2 bg-cyan-600 rounded hover:bg-cyan-500">
            Coba Lagi
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h3 className="text-lg font-semibold text-cyan-400">🕸️ Graph Inteligensi</h3>
          {stats?.collusion_edges > 0 && (
            <p className="text-red-400 text-sm mt-1">
              ⚠️ Terdeteksi {stats.collusion_edges} pola kolusi!
            </p>
          )}
        </div>
        <button onClick={loadData} className="px-3 py-1 bg-cyan-600 rounded hover:bg-cyan-500 text-sm">
          🔄 Refresh
        </button>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-3 gap-4 mb-4 p-3 bg-gray-700/50 rounded">
        <div className="text-center">
          <div className="text-xl font-bold text-cyan-400">{stats?.total_entities || 0}</div>
          <div className="text-xs text-gray-400">Total Entitas</div>
        </div>
        <div className="text-center">
          <div className="text-xl font-bold text-yellow-400">{stats?.total_relationships || 0}</div>
          <div className="text-xs text-gray-400">Total Relasi</div>
        </div>
        <div className="text-center">
          <div className="text-xl font-bold text-red-400">{stats?.collusion_edges || 0}</div>
          <div className="text-xs text-gray-400">Tepi Kolusi</div>
        </div>
      </div>

      {/* Nodes Section */}
      {graphData.nodes.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-300 mb-2">📌 Entitas Terlibat ({graphData.nodes.length})</h4>
          <div className="flex flex-wrap gap-2">
            {graphData.nodes.map((node, idx) => (
              <div key={idx} className="bg-gray-700 rounded-full px-3 py-1 text-sm flex items-center gap-2">
                <span className="text-gray-300">{node.name}</span>
                <span className={`text-xs font-bold ${getRiskColor(node.risk_score)}`}>
                  {node.risk_score}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Relationships Table */}
      <div className="overflow-x-auto">
        <h4 className="text-sm font-semibold text-gray-300 mb-2">🔗 Relasi Antar Entitas ({graphData.edges.length})</h4>
        <table className="w-full text-sm">
          <thead className="bg-gray-700">
            <tr>
              <th className="px-3 py-2 text-left text-gray-300">Sumber</th>
              <th className="px-3 py-2 text-left text-gray-300">Target</th>
              <th className="px-3 py-2 text-left text-gray-300">Jenis</th>
              <th className="px-3 py-2 text-left text-gray-300">Tingkat Keyakinan</th>
            </tr>
          </thead>
          <tbody>
            {graphData.edges.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-center py-4 text-gray-500">Tidak ada relasi ditemukan</td>
              </tr>
            ) : (
              graphData.edges.map((edge, idx) => (
                <tr key={idx} className="border-t border-gray-700 hover:bg-gray-700/30">
                  <td className="px-3 py-2 text-gray-300 font-medium">{edge.source}</td>
                  <td className="px-3 py-2 text-gray-300 font-medium">→ {edge.target}</td>
                  <td className="px-3 py-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${getEdgeBadge(edge.type)}`}>
                      {edge.type === 'collusion' ? '🤝 KOLUSI' : edge.type === 'financial' ? '💰 FINANSIAL' : '🏢 KEPEMILIKAN BERSAMA'}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-gray-600 rounded-full h-1.5">
                        <div 
                          className={`h-1.5 rounded-full ${
                            edge.confidence >= 70 ? 'bg-red-500' : edge.confidence >= 50 ? 'bg-yellow-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${edge.confidence}%` }}
                        ></div>
                      </div>
                      <span className="text-gray-300 text-xs">{edge.confidence}%</span>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
