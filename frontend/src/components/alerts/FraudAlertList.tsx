// src/components/alerts/FraudAlertList.tsx
import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { AlertTriangle, TrendingUp, Building2, Users, DollarSign, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

interface FraudAlert {
  id: string;
  type: 'vendor_collusion' | 'abnormal_bidding' | 'conflict_of_interest' | 'price_anomaly';
  severity: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  entities: string[];
  case_id?: string;
  detected_at: string;
  confidence: number;
}

const FraudAlertList: React.FC = () => {
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    loadFraudAlerts();
    const interval = setInterval(loadFraudAlerts, 60000);
    return () => clearInterval(interval);
  }, []);

  const loadFraudAlerts = async () => {
    try {
      // Mock data - in production, call API
      const mockAlerts: FraudAlert[] = [
        {
          id: '1',
          type: 'vendor_collusion',
          severity: 'high',
          title: 'Potential Vendor Collusion Detected',
          description: 'PT Teknologi Nusantara and CV Solusi Digital share same director and address pattern',
          entities: ['PT Teknologi Nusantara', 'CV Solusi Digital'],
          detected_at: new Date().toISOString(),
          confidence: 92
        },
        {
          id: '2',
          type: 'abnormal_bidding',
          severity: 'medium',
          title: 'Abnormal Bidding Pattern',
          description: 'Multiple bids submitted from same IP address range',
          entities: ['Vendor A', 'Vendor B', 'Vendor C'],
          detected_at: new Date(Date.now() - 86400000).toISOString(),
          confidence: 78
        },
        {
          id: '3',
          type: 'price_anomaly',
          severity: 'low',
          title: 'Price Anomaly Detected',
          description: 'Contract value significantly above market average (35% higher)',
          entities: ['PT Maju Jaya'],
          detected_at: new Date(Date.now() - 172800000).toISOString(),
          confidence: 65
        }
      ];
      setAlerts(mockAlerts);
    } catch (error) {
      console.error('Error loading fraud alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'medium': return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default: return <AlertTriangle className="w-5 h-5 text-blue-500" />;
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 border-red-200';
      case 'medium': return 'bg-yellow-100 border-yellow-200';
      default: return 'bg-blue-100 border-blue-200';
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'vendor_collusion': return 'Vendor Collusion';
      case 'abnormal_bidding': return 'Abnormal Bidding';
      case 'conflict_of_interest': return 'Conflict of Interest';
      case 'price_anomaly': return 'Price Anomaly';
      default: return type;
    }
  };

  const filteredAlerts = filter === 'all' ? alerts : alerts.filter(a => a.severity === filter);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-20 bg-gray-100 rounded"></div>
          <div className="h-20 bg-gray-100 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-red-500" />
          <h3 className="text-lg font-semibold text-gray-900">Fraud Detection Alerts</h3>
          {alerts.filter(a => a.severity === 'high').length > 0 && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-red-500 text-white">
              {alerts.filter(a => a.severity === 'high').length} High
            </span>
          )}
        </div>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="text-sm border border-gray-300 rounded-md px-2 py-1"
        >
          <option value="all">All</option>
          <option value="high">High Severity</option>
          <option value="medium">Medium Severity</option>
          <option value="low">Low Severity</option>
        </select>
      </div>

      <div className="divide-y divide-gray-200 max-h-96 overflow-auto">
        {filteredAlerts.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <AlertTriangle className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No fraud alerts detected</p>
            <p className="text-sm">System is monitoring for suspicious activities</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => (
            <div key={alert.id} className={`p-4 hover:bg-gray-50 ${getSeverityBg(alert.severity)}`}>
              <div className="flex items-start gap-3">
                {getSeverityIcon(alert.severity)}
                <div className="flex-1">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div>
                      <h4 className="font-medium text-gray-900">{alert.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(alert.detected_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="mt-2 flex items-center gap-3 flex-wrap">
                    <div className="flex items-center gap-1">
                      <Building2 className="w-3 h-3 text-gray-400" />
                      <span className="text-xs text-gray-500">
                        {alert.entities.join(', ')}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3 text-gray-400" />
                      <span className="text-xs text-gray-500">
                        Confidence: {alert.confidence}%
                      </span>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      alert.severity === 'high' ? 'bg-red-100 text-red-700' :
                      alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {alert.severity.toUpperCase()}
                    </span>
                    <button className="text-blue-600 hover:text-blue-800 text-xs flex items-center gap-1">
                      <Eye className="w-3 h-3" /> Investigate
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default FraudAlertList;