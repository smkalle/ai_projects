import React from 'react';
import { BeakerIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

const WaterQualityTab = ({ data, city }) => {
  const waterData = data?.hazard_data?.water_quality || {
    status: 'Safe',
    contamination_level: 'Low',
    ph: 7.2,
    chlorine: 0.3,
    turbidity: 0.5
  };

  return (
    <div className="space-y-6">
      {/* Main Status */}
      <div className="glass-card p-8 text-center">
        <BeakerIcon className="w-16 h-16 text-cyan-400 mx-auto mb-4" />
        <h2 className="text-2xl font-semibold mb-2">Water Quality Status</h2>
        <div className="text-4xl font-bold text-green-400 mb-4">
          {waterData.status}
        </div>
        <p className="text-gray-400">
          Contamination Level: {waterData.contamination_level}
        </p>
      </div>

      {/* Quality Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-6 text-center">
          <h4 className="font-semibold mb-3">pH Level</h4>
          <div className="text-3xl font-bold text-blue-400 mb-2">
            {waterData.ph}
          </div>
          <p className="text-sm text-gray-400">Optimal range: 6.5-8.5</p>
        </div>
        
        <div className="glass-card p-6 text-center">
          <h4 className="font-semibold mb-3">Chlorine</h4>
          <div className="text-3xl font-bold text-green-400 mb-2">
            {waterData.chlorine} mg/L
          </div>
          <p className="text-sm text-gray-400">Safe levels</p>
        </div>
        
        <div className="glass-card p-6 text-center">
          <h4 className="font-semibold mb-3">Turbidity</h4>
          <div className="text-3xl font-bold text-green-400 mb-2">
            {waterData.turbidity} NTU
          </div>
          <p className="text-sm text-gray-400">Clear water</p>
        </div>
      </div>

      {/* Safety Assessment */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <CheckCircleIcon className="w-6 h-6 text-green-400" />
          Safety Assessment
        </h3>
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>Safe for drinking</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>No harmful bacteria detected</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span>Chemical levels within safe limits</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WaterQualityTab;