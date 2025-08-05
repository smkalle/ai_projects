import React from 'react';
import { XMarkIcon, CheckIcon } from '@heroicons/react/24/outline';

const NotificationDropdown = ({ notifications, onClose }) => {
  const getTypeColor = (type) => {
    switch (type) {
      case 'warning': return 'text-yellow-400 bg-yellow-500/20';
      case 'error': return 'text-red-400 bg-red-500/20';
      case 'success': return 'text-green-400 bg-green-500/20';
      default: return 'text-blue-400 bg-blue-500/20';
    }
  };

  const formatTime = (time) => {
    const date = new Date(time);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="absolute right-0 mt-2 w-80 glass-card rounded-xl shadow-xl border border-white/10 animate-slide-up">
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Notifications</h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-white/10 transition-colors"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-3 max-h-96 overflow-y-auto">
          {notifications.length === 0 ? (
            <p className="text-gray-400 text-center py-8">No notifications</p>
          ) : (
            notifications.map((notification) => (
              <div
                key={notification.id}
                className={`p-3 rounded-lg border transition-all ${
                  notification.read 
                    ? 'bg-white/5 border-white/10' 
                    : 'bg-white/10 border-white/20'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className={`w-2 h-2 rounded-full mt-2 ${getTypeColor(notification.type)}`} />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm">{notification.title}</p>
                    <p className="text-gray-400 text-xs mt-1">{notification.message}</p>
                    <p className="text-gray-500 text-xs mt-2">{formatTime(notification.time)}</p>
                  </div>
                  {!notification.read && (
                    <div className="w-2 h-2 bg-primary-400 rounded-full animate-pulse" />
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {notifications.some(n => !n.read) && (
          <button className="w-full mt-4 glass-button py-2 text-sm flex items-center justify-center gap-2">
            <CheckIcon className="w-4 h-4" />
            Mark all as read
          </button>
        )}
      </div>
    </div>
  );
};

export default NotificationDropdown;