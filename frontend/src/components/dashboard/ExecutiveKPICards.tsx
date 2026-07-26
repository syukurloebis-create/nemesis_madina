import React from 'react';
import { TrendingUp, TrendingDown, AlertCircle, CheckCircle, Database, Users, FileText, Shield } from 'lucide-react';

interface KPI {
  label: string;
  value: number | string;
  change?: number;
  icon: React.ReactNode;
  color: string;
}

interface ExecutiveKPICardsProps {
  cases: any;
  fraud: any;
  graph: any;
  risk: any;
  loading?: boolean;
}

export const ExecutiveKPICards: React.FC<ExecutiveKPICardsProps> = ({
  cases,
  fraud,
  graph,
  risk,
  loading = false,
}) => {
  const kpis: KPI[] = [
    {
      label: 'Total Cases',
      value: cases?.total ?? 0,
      change: 5,
      icon: <FileText className="w-5 h-5" />,
      color: 'blue',
    },
    {
      label: 'Active Alerts',
      value: fraud?.active_alerts ?? 0,
      change: -12,
      icon: <AlertCircle className="w-5 h-5" />,
      color: 'red',
    },
    {
      label: 'Risk Score',
      value: `${risk?.total_risk ?? 0}%`,
      change: 3,
      icon: <Shield className="w-5 h-5" />,
      color: 'orange',
    },
    {
      label: 'Graph Entities',
      value: graph?.total_entities ?? 0,
      change: 8,
      icon: <Database className="w-5 h-5" />,
      color: 'purple',
    },
  ];

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="animate-pulse bg-gray-800/50 rounded-xl p-6 h-32" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpis.map((kpi, index) => (
        <KPICard key={index} {...kpi} />
      ))}
    </div>
  );
};

interface KPICardProps {
  label: string;
  value: number | string;
  change?: number;
  icon: React.ReactNode;
  color: string;
}

function KPICard({ label, value, change, icon, color }: KPICardProps) {
  const colors = {
    blue: 'border-blue-500/20 bg-blue-500/10',
    red: 'border-red-500/20 bg-red-500/10',
    orange: 'border-orange-500/20 bg-orange-500/10',
    purple: 'border-purple-500/20 bg-purple-500/10',
    green: 'border-green-500/20 bg-green-500/10',
  };

  const textColors = {
    blue: 'text-blue-400',
    red: 'text-red-400',
    orange: 'text-orange-400',
    purple: 'text-purple-400',
    green: 'text-green-400',
  };

  return (
    <div className={`rounded-xl border p-5 ${colors[color as keyof typeof colors]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
          {change !== undefined && (
            <div className="flex items-center gap-1 mt-1">
              {change > 0 ? (
                <TrendingUp className="w-3 h-3 text-green-400" />
              ) : (
                <TrendingDown className="w-3 h-3 text-red-400" />
              )}
              <span className={`text-xs ${change > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {Math.abs(change)}%
              </span>
            </div>
          )}
        </div>
        <div className={`p-2 rounded-lg ${textColors[color as keyof typeof textColors]} bg-black/20`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

export default ExecutiveKPICards;
