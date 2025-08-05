import React from 'react';
import { ExclamationTriangleIcon, ClockIcon, MapPinIcon } from '@heroicons/react/24/outline';

const AlertsPanel = ({ cities, showAll = false }) => {
  // Mock alerts data
  const mockAlerts = [
    {
      id: 1,
      city: 'Tokyo, Japan',
      type: 'Air Quality',
      severity: 'moderate',
      message: 'Air quality has reached moderate levels (AQI: 75)',
      time: '15 minutes ago',
      icon: '🗼'
    },
    {
      id: 2,
      city: 'Mumbai, India',
      type: 'Water Quality',
      severity: 'high',
      message: 'Water contamination detected in local supply',
      time: '1 hour ago',
      icon: '🏛️'
    },
    {
      id: 3,
      city: 'São Paulo, Brazil',
      type: 'Weather',
      severity: 'low',
      message: 'Heavy rainfall expected in the next 24 hours',
      time: '2 hours ago',
      icon: '🌆'
    }
  ];

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'text-red-400 bg-red-500/20 border-red-500/30';
      case 'moderate': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      case 'low': return 'text-blue-400 bg-blue-500/20 border-blue-500/30';
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/30';
    }
  };

  const displayAlerts = showAll ? mockAlerts : mockAlerts.slice(0, 3);

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold flex items-center gap-2">
          <ExclamationTriangleIcon className="w-6 h-6 text-yellow-400" />
          {showAll ? 'All Active Alerts' : 'Recent Alerts'}
        </h3>
        {!showAll && mockAlerts.length > 3 && (
          <button className="text-primary-400 hover:text-primary-300 text-sm font-medium">
            View All ({mockAlerts.length})
          </button>
        )}
      </div>

      <div className="space-y-4">
        {displayAlerts.length === 0 ? (
          <div className="text-center py-8">
            <ExclamationTriangleIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-400">No active alerts</p>
          </div>
        ) : (
          displayAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-xl border transition-all hover:scale-[1.02] ${getSeverityColor(alert.severity)}`}
            >
              <div className="flex items-start gap-4">
                <div className="text-2xl">{alert.icon}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold text-white">{alert.type}</h4>
                    <span className="text-xs px-2 py-1 rounded-full bg-white/10 uppercase tracking-wide">
                      {alert.severity}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-300 mb-2">
                    <MapPinIcon className="w-4 h-4" />
                    <span>{alert.city}</span>
                  </div>
                  <p className="text-gray-300 text-sm">{alert.message}</p>
                  <div className="flex items-center gap-2 mt-3 text-xs text-gray-400">
                    <ClockIcon className="w-4 h-4" />
                    <span>{alert.time}</span>
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

export default AlertsPanel;