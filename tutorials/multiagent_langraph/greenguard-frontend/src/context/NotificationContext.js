import React, { createContext, useContext, useState } from 'react';

const NotificationContext = createContext();

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: 'Air Quality Alert',
      message: 'AQI in Tokyo has reached moderate levels',
      type: 'warning',
      time: new Date().toISOString(),
      read: false
    },
    {
      id: 2,
      title: 'System Update',
      message: 'GreenGuard v3.0 is now live with new features',
      type: 'info',
      time: new Date().toISOString(),
      read: false
    }
  ]);

  const unreadCount = notifications.filter(n => !n.read).length;

  const addNotification = (notification) => {
    setNotifications(prev => [{
      id: Date.now(),
      ...notification,
      time: new Date().toISOString(),
      read: false
    }, ...prev]);
  };

  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(n => ({ ...n, read: true }))
    );
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const value = {
    notifications,
    unreadCount,
    addNotification,
    markAsRead,
    markAllAsRead,
    removeNotification
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};