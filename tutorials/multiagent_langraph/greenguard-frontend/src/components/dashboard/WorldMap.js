import React from 'react';
import { MapPinIcon } from '@heroicons/react/24/outline';

const WorldMap = ({ cities }) => {
  return (
    <div className="relative">
      <h3 className="text-lg font-semibold mb-6">Global Environmental Status</h3>
      
      {/* Simplified world map representation */}
      <div className="relative bg-gradient-to-br from-blue-900/20 to-green-900/20 rounded-2xl p-8 min-h-[400px] flex items-center justify-center">
        <div className="text-center">
          <MapPinIcon className="w-16 h-16 text-primary-400 mx-auto mb-4" />
          <h4 className="text-xl font-semibold mb-2">Interactive World Map</h4>
          <p className="text-gray-400 mb-6">
            Coming soon: Interactive map with real-time city markers
          </p>
          
          {/* City status grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 max-w-md mx-auto">
            {cities.slice(0, 6).map((city) => (
              <div key={city.id} className="glass-card p-3 text-center">
                <div className="text-2xl mb-1">{city.icon}</div>
                <div className="text-sm font-medium text-white">{city.name.split(',')[0]}</div>
                <div className={`text-xs mt-1 ${
                  city.aqi <= 50 ? 'text-green-400' : 
                  city.aqi <= 100 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  AQI {city.aqi}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Legend */}
      <div className="flex justify-center mt-6">
        <div className="flex gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-400 rounded-full"></div>
            <span>Good (0-50)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
            <span>Moderate (51-100)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-400 rounded-full"></div>
            <span>Unhealthy (101+)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorldMap;