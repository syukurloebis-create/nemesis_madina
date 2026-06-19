// KPICards.tsx - Dashboard KPI Cards with Dark Mode
import React from 'react';
import {
  Activity,
  AlertTriangle,
  Shield,
  CheckCircle,
} from 'lucide-react';

interface KPICardsProps {
  data: {
    totalCases: number;
    criticalRisk: number;
    highRisk: number;
    evidenceTotal: number;
    evidenceVerified: number;
  };
  className?: string;
}

export const KPICards: React.FC<KPICardsProps> = ({ data, className = '' }) => {
  const cards = [
    {
      label: 'Total Cases',
      value: data.totalCases,
      icon: Activity,
      color: 'text-blue-500 dark:text-blue-400',
      bg: 'bg-blue-50 dark:bg-blue-900/20',
    },
    {
      label: 'Critical Risk',
      value: data.criticalRisk,
      icon: AlertTriangle,
      color: 'text-red-500 dark:text-red-400',
      bg: 'bg-red-50 dark:bg-red-900/20',
    },
    {
      label: 'Evidence',
      value: data.evidenceTotal,
      icon: Shield,
      color: 'text-green-500 dark:text-green-400',
      bg: 'bg-green-50 dark:bg-green-900/20',
    },
    {
      label: 'Verified',
      value: data.evidenceVerified,
      icon: CheckCircle,
      color: 'text-emerald-500 dark:text-emerald-400',
      bg: 'bg-emerald-50 dark:bg-emerald-900/20',
    },
  ];

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}>
      {cards.map((card, index) => (
        <div
          key={index}
          className="bg-white dark:bg-dark-card rounded-lg shadow p-4 hover:shadow-md transition-all duration-200 border border-gray-100 dark:border-dark-border"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">{card.label}</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{card.value}</p>
            </div>
            <div className={`p-2 rounded-lg ${card.bg}`}>
              <card.icon className={`w-5 h-5 ${card.color}`} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default KPICards;
