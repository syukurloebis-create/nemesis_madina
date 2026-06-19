import React from 'react';
import LiveAlertStream from '../components/alerts/LiveAlertStream';

const LiveAlerts: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <h1 className="text-2xl font-bold text-white">Live Alert Center</h1>
        <p className="text-gray-400 text-sm mt-1">Real-time threat detection and alert monitoring</p>
      </div>
      
      <LiveAlertStream />
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <h3 className="text-sm font-semibold text-gray-400 mb-2">Alert Categories</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>🔴 Critical</span>
              <span className="text-red-400">High priority threats</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>🟠 High</span>
              <span className="text-orange-400">Urgent investigation</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>🟡 Medium</span>
              <span className="text-yellow-400">Needs review</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>🟢 Low</span>
              <span className="text-green-400">Informational</span>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <h3 className="text-sm font-semibold text-gray-400 mb-2">Alert Actions</h3>
          <div className="space-y-2 text-sm text-gray-400">
            <p>✅ Click on alert to acknowledge</p>
            <p>🔄 Auto-refresh every 5 seconds</p>
            <p>🔔 Real-time WebSocket connection</p>
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <h3 className="text-sm font-semibold text-gray-400 mb-2">Integration Status</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>WebSocket</span>
              <span className="text-green-400">● Active</span>
            </div>
            <div className="flex justify-between">
              <span>Alert Engine</span>
              <span className="text-green-400">● Running</span>
            </div>
            <div className="flex justify-between">
              <span>Notification</span>
              <span className="text-yellow-400">○ Configured</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveAlerts;
