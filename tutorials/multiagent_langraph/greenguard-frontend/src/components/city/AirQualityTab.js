import React from 'react';
import { CloudIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const AirQualityTab = ({ data, city }) => {
  const aqi = data?.hazard_data?.air_quality?.aqi || 45;
  const pm25 = data?.hazard_data?.air_quality?.pm2_5 || 12;
  const status = data?.hazard_data?.air_quality?.status || 'Good';

  const getAQIColor = (aqi) => {
    if (aqi <= 50) return 'text-green-400';
    if (aqi <= 100) return 'text-yellow-400';
    if (aqi <= 150) return 'text-orange-400';
    return 'text-red-400';
  };

  const getHealthAdvice = (aqi) => {
    if (aqi <= 50) return 'Air quality is satisfactory, and air pollution poses little or no risk.';
    if (aqi <= 100) return 'Air quality is acceptable for most people. Unusually sensitive people should consider limiting prolonged outdoor exertion.';
    if (aqi <= 150) return 'Members of sensitive groups may experience health effects. The general public is less likely to be affected.';
    return 'Health alert: The risk of health effects is increased for everyone.';
  };

  return (
    <div className="space-y-6">
      {/* Main AQI Display */}
      <div className="glass-card p-8 text-center">
        <CloudIcon className="w-16 h-16 text-primary-400 mx-auto mb-4" />
        <h2 className="text-2xl font-semibold mb-2">Air Quality Index</h2>
        <div className={`text-6xl font-bold mb-4 ${getAQIColor(aqi)}`}>
          {aqi}
        </div>
        <p className={`text-xl font-medium ${getAQIColor(aqi)}`}>
          {status}
        </p>
        <p className="text-gray-400 mt-4">
          Last updated: {new Date().toLocaleString()}
        </p>
      </div>

      {/* Pollutant Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Pollutant Levels</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span>PM2.5</span>
              <span className={getAQIColor(aqi)}>{pm25} μg/m³</span>
            </div>
            <div className="flex justify-between items-center">
              <span>PM10</span>
              <span className="text-green-400">18 μg/m³</span>
            </div>
            <div className="flex justify-between items-center">
              <span>NO₂</span>
              <span className="text-yellow-400">25 μg/m³</span>
            </div>
            <div className="flex justify-between items-center">
              <span>O₃</span>
              <span className="text-green-400">85 μg/m³</span>
            </div>
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold mb-4">Health Recommendations</h3>
          <div className="flex items-start gap-3">
            <ExclamationTriangleIcon className={`w-6 h-6 mt-1 ${getAQIColor(aqi)}`} />
            <p className="text-gray-300 text-sm leading-relaxed">
              {getHealthAdvice(aqi)}
            </p>
          </div>
        </div>
      </div>

      {/* 24-Hour Trend */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-4">24-Hour AQI Trend</h3>
        <div className="h-48 flex items-center justify-center text-gray-400">
          <p>Chart visualization coming soon...</p>
        </div>
      </div>
    </div>
  );
};

export default AirQualityTab;