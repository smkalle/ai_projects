import React from 'react';
import { Link } from 'react-router-dom';
import { MapPinIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const CityCard = ({ city }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'good': return 'bg-green-500';
      case 'moderate': return 'bg-yellow-500';
      case 'unhealthy': return 'bg-orange-500';
      case 'hazardous': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getAQIColor = (aqi) => {
    if (aqi <= 50) return 'text-green-400';
    if (aqi <= 100) return 'text-yellow-400';
    if (aqi <= 150) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <Link to={`/city/${city.id}`} className="block group">
      <div className="metric-card relative overflow-hidden">
        {/* Status Indicator */}
        <div className={`absolute top-0 right-0 w-16 h-16 ${getStatusColor(city.status)} opacity-20 rounded-bl-full`} />
        
        {/* City Icon */}
        <div className="text-4xl mb-3">{city.icon}</div>
        
        {/* City Name */}
        <h3 className="font-semibold text-lg text-white group-hover:text-primary-400 transition-colors">
          {city.name}
        </h3>
        
        {/* Location */}
        <div className="flex items-center gap-1 text-gray-400 text-sm mt-1">
          <MapPinIcon className="w-4 h-4" />
          <span>Live Monitoring</span>
        </div>
        
        {/* AQI Display */}
        <div className="mt-4">
          <p className="text-gray-400 text-sm">Air Quality Index</p>
          <p className={`text-3xl font-bold ${getAQIColor(city.aqi)}`}>
            {city.aqi}
          </p>
        </div>
        
        {/* Alerts */}
        {city.alerts > 0 && (
          <div className="flex items-center gap-2 mt-4 text-orange-400">
            <ExclamationTriangleIcon className="w-5 h-5" />
            <span className="text-sm font-medium">{city.alerts} Active Alerts</span>
          </div>
        )}
        
        {/* Hover Effect */}
        <div className="absolute inset-0 bg-gradient-to-t from-primary-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
      </div>
    </Link>
  );
};

export default CityCard;