/**
 * Real-time Alert Feed Component
 * Displays system alerts in real-time
 */
import React, { useState, useEffect, useRef } from 'react';
import { Bell, AlertCircle, CheckCircle, Info, X, AlertTriangle, Clock } from 'lucide-react';
import websocket from '../../services/websocket';

interface Alert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  source?: string;
  actions?: {
    label: string;
    onClick: () => void;
  }[];
}

export const AlertFeed: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isExpanded, setIsExpanded] = useState(false);
  const feedRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Subscribe to real-time alerts
    const unsubscribe = websocket.onAlert((data) => {
      const newAlert: Alert = {
        id: data.id || Date.now().toString(),
        type: data.severity || 'info',
        title: data.title || 'Alert',
        message: data.message || 'No message provided',
        timestamp: data.timestamp || new Date().toISOString(),
        read: false,
        source: data.source,
        actions: data.actions
      };
      
      setAlerts(prev => [newAlert, ...prev].slice(0, 50)); // Keep last 50 alerts
      setUnreadCount(prev => prev + 1);

      // Auto-mark as read after 10 seconds if not expanded
      if (!isExpanded) {
        setTimeout(() => {
          markAsRead(newAlert.id);
        }, 10000);
      }
    });

    // Load initial alerts
    loadInitialAlerts();

    return () => {
      unsubscribe();
    };
  }, [isExpanded]);

  const loadInitialAlerts = async () => {
    try {
      const response = await fetch('/api/v1/alerts?limit=20');
      const data = await response.json();
      if (data.alerts) {
        setAlerts(data.alerts.map((alert: any) => ({
          ...alert,
          read: alert.read || false
        })));
        setUnreadCount(data.alerts.filter((a: any) => !a.read).length);
      }
    } catch (error) {
      console.error('Failed to load alerts:', error);
    }
  };

  const markAsRead = (alertId: string) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId ? { ...alert, read: true } : alert
      )
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = () => {
    setAlerts(prev => 
      prev.map(alert => ({ ...alert, read: true }))
    );
    setUnreadCount(0);
  };

  const dismissAlert = (alertId: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      default:
        return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  const getTypeStyles = (type: string) => {
    switch (type) {
      case 'error':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      case 'warning':
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
      case 'success':
        return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      default:
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800';
    }
  };

  return (
    <div className="relative">
      {/* Bell Icon with Badge */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="relative p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
      >
        <Bell className="w-6 h-6 text-gray-600 dark:text-gray-400" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isExpanded && (
        <div className="absolute right-0 mt-2 w-96 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden z-50">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <Bell className="w-4 h-4" />
              Alerts
              {unreadCount > 0 && (
                <span className="text-xs bg-red-500 text-white px-2 py-0.5 rounded-full">
                  {unreadCount} unread
                </span>
              )}
            </h3>
            <div className="flex gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400"
                >
                  Mark all read
                </button>
              )}
              <button
                onClick={() => setIsExpanded(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Alert List */}
          <div ref={feedRef} className="max-h-96 overflow-y-auto">
            {alerts.length === 0 ? (
              <div className="flex items-center justify-center py-8 text-gray-500 dark:text-gray-400">
                <CheckCircle className="w-6 h-6 mr-2" />
                No alerts
              </div>
            ) : (
              alerts.map((alert) => (
                <AlertItem
                  key={alert.id}
                  alert={alert}
                  onMarkRead={markAsRead}
                  onDismiss={dismissAlert}
                  getIcon={getIcon}
                  getTypeStyles={getTypeStyles}
                />
              ))
            )}
          </div>

          {/* Footer */}
          <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700 text-center">
            <button
              onClick={() => window.location.href = '/alerts'}
              className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
            >
              View all alerts
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

interface AlertItemProps {
  alert: Alert;
  onMarkRead: (id: string) => void;
  onDismiss: (id: string) => void;
  getIcon: (type: string) => React.ReactNode;
  getTypeStyles: (type: string) => string;
}

const AlertItem: React.FC<AlertItemProps> = ({
  alert,
  onMarkRead,
  onDismiss,
  getIcon,
  getTypeStyles
}) => {
  return (
    <div
      className={`
        relative px-4 py-3 border-b border-gray-100 dark:border-gray-700
        ${!alert.read ? 'bg-blue-50/50 dark:bg-blue-900/10' : ''}
        hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors
      `}
      onClick={() => !alert.read && onMarkRead(alert.id)}
    >
      <div className="flex gap-3">
        <div className="flex-shrink-0 mt-0.5">
          {getIcon(alert.type)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {alert.title}
            </p>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDismiss(alert.id);
              }}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
            {alert.message}
          </p>
          <div className="flex items-center gap-2 mt-1.5 text-xs text-gray-500 dark:text-gray-500">
            <Clock className="w-3 h-3" />
            <span>{formatTime(alert.timestamp)}</span>
            {alert.source && (
              <>
                <span>•</span>
                <span>{alert.source}</span>
              </>
            )}
            {!alert.read && (
              <>
                <span>•</span>
                <span className="text-blue-600 dark:text-blue-400">New</span>
              </>
            )}
          </div>
          {alert.actions && (
            <div className="flex gap-2 mt-2">
              {alert.actions.map((action, index) => (
                <button
                  key={index}
                  onClick={(e) => {
                    e.stopPropagation();
                    action.onClick();
                  }}
                  className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 transition-colors"
                >
                  {action.label}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
  return date.toLocaleDateString();
}