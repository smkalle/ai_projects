import React from 'react';
import { ExclamationTriangleIcon, ClockIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline';

const AlertsTab = ({ data, city }) => {
  // Mock alerts specific to the city
  const cityAlerts = [
    {
      id: 1,
      type: 'Air Quality',
      severity: 'moderate',
      status: 'active',
      title: 'Moderate Air Quality Alert',
      message: 'Air quality levels have reached moderate levels. Sensitive individuals should limit outdoor activities.',
      timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      source: 'Environmental Monitoring Station'
    },
    {
      id: 2,
      type: 'Water Quality',
      severity: 'low',
      status: 'resolved',
      title: 'Water Quality Advisory Lifted',
      message: 'Previous water quality concerns have been resolved. Water is now safe for consumption.',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      source: 'Municipal Water Department'
    },
    {
      id: 3,
      type: 'Weather',
      severity: 'high',
      status: 'active',
      title: 'Severe Weather Warning',
      message: 'Heavy rainfall and strong winds expected in the next 6 hours. Take necessary precautions.',
      timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
      source: 'National Weather Service'
    }
  ];

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'border-red-500/50 bg-red-500/10 text-red-400';
      case 'moderate': return 'border-yellow-500/50 bg-yellow-500/10 text-yellow-400';
      case 'low': return 'border-blue-500/50 bg-blue-500/10 text-blue-400';
      default: return 'border-gray-500/50 bg-gray-500/10 text-gray-400';
    }
  };

  const getStatusIcon = (status) => {
    return status === 'active' ? 
      <ExclamationTriangleIcon className="w-5 h-5" /> : 
      <CheckCircleIcon className="w-5 h-5" />;
  };

  const getStatusColor = (status) => {
    return status === 'active' ? 'text-orange-400' : 'text-green-400';
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / 60000);
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes} minutes ago`;
    } else if (diffInMinutes < 1440) {
      return `${Math.floor(diffInMinutes / 60)} hours ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const activeAlerts = cityAlerts.filter(alert => alert.status === 'active');
  const resolvedAlerts = cityAlerts.filter(alert => alert.status === 'resolved');

  return (
    <div className="space-y-6">
      {/* Alert Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-6 text-center">
          <ExclamationTriangleIcon className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h4 className="font-semibold mb-2">Active Alerts</h4>
          <div className="text-3xl font-bold text-red-400">
            {activeAlerts.length}
          </div>
        </div>
        
        <div className="glass-card p-6 text-center">
          <CheckCircleIcon className="w-12 h-12 text-green-400 mx-auto mb-4" />
          <h4 className="font-semibold mb-2">Resolved Today</h4>
          <div className="text-3xl font-bold text-green-400">
            {resolvedAlerts.length}
          </div>
        </div>
        
        <div className="glass-card p-6 text-center">
          <ClockIcon className="w-12 h-12 text-blue-400 mx-auto mb-4" />
          <h4 className="font-semibold mb-2">Avg Response</h4>
          <div className="text-3xl font-bold text-blue-400">
            2.3h
          </div>
        </div>
      </div>

      {/* Active Alerts */}
      {activeAlerts.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <ExclamationTriangleIcon className="w-6 h-6 text-red-400" />
            Active Alerts
          </h3>
          <div className="space-y-4">
            {activeAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-4 rounded-xl border-2 ${getSeverityColor(alert.severity)}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={getStatusColor(alert.status)}>
                      {getStatusIcon(alert.status)}
                    </div>
                    <div>
                      <h4 className="font-semibold text-white">{alert.title}</h4>
                      <span className="text-sm text-gray-400">{alert.type}</span>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium uppercase ${getSeverityColor(alert.severity)}`}>
                    {alert.severity}
                  </span>
                </div>
                <p className="text-gray-300 mb-3">{alert.message}</p>
                <div className="flex items-center justify-between text-sm text-gray-400">
                  <span>Source: {alert.source}</span>
                  <span>{formatTimestamp(alert.timestamp)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="glass-card p-6">
        <h3 className="text-xl font-semibold mb-6">Recent Activity</h3>
        <div className="space-y-4">
          {cityAlerts.map((alert) => (
            <div key={`activity-${alert.id}`} className="flex items-start gap-4 p-4 rounded-lg bg-white/5 border border-gray-700">
              <div className={getStatusColor(alert.status)}>
                {getStatusIcon(alert.status)}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-medium text-white">{alert.title}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs ${getSeverityColor(alert.severity)}`}>
                    {alert.severity}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-2">{alert.message}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>{alert.type}</span>
                  <span>•</span>
                  <span>{formatTimestamp(alert.timestamp)}</span>
                  <span>•</span>
                  <span className={getStatusColor(alert.status)}>
                    {alert.status.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AlertsTab;