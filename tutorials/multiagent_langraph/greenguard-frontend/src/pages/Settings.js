import React from 'react';
import { Cog6ToothIcon } from '@heroicons/react/24/outline';

const Settings = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-6">
          <Cog6ToothIcon className="w-8 h-8 text-primary-400" />
          <h1 className="text-3xl font-bold">Settings</h1>
        </div>
        
        <p className="text-gray-400">Settings page coming soon...</p>
      </div>
    </div>
  );
};

export default Settings;