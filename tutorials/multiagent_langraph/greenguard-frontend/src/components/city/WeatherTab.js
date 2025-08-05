import React from 'react';
import { CloudIcon, SunIcon, EyeIcon, ThermometerIcon } from '@heroicons/react/24/outline';

const WeatherTab = ({ data, city }) => {
  const weatherData = data?.hazard_data?.weather || {
    temperature: 22,
    humidity: 65,
    wind_speed: 12,
    visibility: 10,
    condition: 'Partly Cloudy',
    uv_index: 6
  };

  const getUVColor = (uv) => {
    if (uv <= 2) return 'text-green-400';
    if (uv <= 5) return 'text-yellow-400';
    if (uv <= 7) return 'text-orange-400';
    if (uv <= 10) return 'text-red-400';
    return 'text-purple-400';
  };

  const getUVDescription = (uv) => {
    if (uv <= 2) return 'Low - Safe for outdoor activities';
    if (uv <= 5) return 'Moderate - Seek shade during midday';
    if (uv <= 7) return 'High - Protection required';
    if (uv <= 10) return 'Very High - Extra protection needed';
    return 'Extreme - Avoid sun exposure';
  };

  return (
    <div className="space-y-6">
      {/* Current Conditions */}
      <div className="glass-card p-8 text-center">
        <CloudIcon className="w-16 h-16 text-blue-400 mx-auto mb-4" />
        <h2 className="text-2xl font-semibold mb-2">Current Weather</h2>
        <div className="text-5xl font-bold text-white mb-2">
          {weatherData.temperature}°C
        </div>
        <p className="text-xl text-gray-300 mb-4">
          {weatherData.condition}
        </p>
        <p className="text-gray-400">
          Last updated: {new Date().toLocaleString()}
        </p>
      </div>

      {/* Weather Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card p-6 text-center">
          <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">💧</span>
          </div>
          <h4 className="font-semibold mb-2">Humidity</h4>
          <div className="text-2xl font-bold text-blue-400">
            {weatherData.humidity}%
          </div>
        </div>
        
        <div className="glass-card p-6 text-center">
          <div className="w-12 h-12 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">💨</span>
          </div>
          <h4 className="font-semibold mb-2">Wind Speed</h4>
          <div className="text-2xl font-bold text-gray-400">
            {weatherData.wind_speed} km/h
          </div>
        </div>
        
        <div className="glass-card p-6 text-center">
          <EyeIcon className="w-12 h-12 text-green-400 mx-auto mb-4" />
          <h4 className="font-semibold mb-2">Visibility</h4>
          <div className="text-2xl font-bold text-green-400">
            {weatherData.visibility} km
          </div>
        </div>
        
        <div className="glass-card p-6 text-center">
          <SunIcon className={`w-12 h-12 mx-auto mb-4 ${getUVColor(weatherData.uv_index)}`} />
          <h4 className="font-semibold mb-2">UV Index</h4>
          <div className={`text-2xl font-bold ${getUVColor(weatherData.uv_index)}`}>
            {weatherData.uv_index}
          </div>
        </div>
      </div>

      {/* UV Advisory */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <SunIcon className={`w-6 h-6 ${getUVColor(weatherData.uv_index)}`} />
          UV Advisory
        </h3>
        <div className={`p-4 rounded-lg border ${getUVColor(weatherData.uv_index)} bg-opacity-10`}>
          <p className="font-medium mb-2">UV Level: {weatherData.uv_index}</p>
          <p className="text-gray-300">{getUVDescription(weatherData.uv_index)}</p>
        </div>
      </div>

      {/* 7-Day Forecast */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-4">7-Day Forecast</h3>
        <div className="space-y-3">
          {['Today', 'Tomorrow', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map((day, index) => (
            <div key={day} className="flex items-center justify-between py-2 border-b border-gray-700 last:border-b-0">
              <span className="font-medium">{day}</span>
              <div className="flex items-center gap-4">
                <span className="text-2xl">☁️</span>
                <span className="text-sm text-gray-400 w-24">Partly Cloudy</span>
                <span className="font-semibold text-white">
                  {22 + (Math.random() * 10 - 5).toFixed(0)}°C
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WeatherTab;