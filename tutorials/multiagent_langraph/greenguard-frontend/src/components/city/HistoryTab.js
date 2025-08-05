import React, { useState } from 'react';
import { ChartBarIcon, CalendarIcon, TrendingUpIcon, TrendingDownIcon } from '@heroicons/react/24/outline';

const HistoryTab = ({ data, city }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('aqi');

  // Mock historical data
  const historicalData = {
    aqi: {
      '7d': [45, 52, 38, 67, 43, 55, 41],
      '30d': [45, 52, 38, 67, 43, 55, 41, 48, 62, 39, 71, 46, 58, 42, 49, 61, 37, 69, 44, 56, 40, 47, 63, 36, 68, 45, 57, 41, 50, 64],
      '1y': Array.from({length: 52}, (_, i) => 30 + Math.random() * 40)
    },
    temperature: {
      '7d': [22, 24, 21, 26, 23, 25, 20],
      '30d': Array.from({length: 30}, (_, i) => 18 + Math.random() * 12),
      '1y': Array.from({length: 52}, (_, i) => 15 + Math.random() * 15)
    },
    humidity: {
      '7d': [65, 70, 58, 72, 63, 68, 60],
      '30d': Array.from({length: 30}, (_, i) => 50 + Math.random() * 30),
      '1y': Array.from({length: 52}, (_, i) => 45 + Math.random() * 35)
    }
  };

  const getMetricLabel = (metric) => {
    const labels = {
      aqi: 'Air Quality Index',
      temperature: 'Temperature (°C)',
      humidity: 'Humidity (%)'
    };
    return labels[metric] || metric;
  };

  const calculateTrend = (data) => {
    if (data.length < 2) return { value: 0, direction: 'stable' };
    const recent = data.slice(-3).reduce((a, b) => a + b, 0) / 3;
    const previous = data.slice(-6, -3).reduce((a, b) => a + b, 0) / 3;
    const change = ((recent - previous) / previous * 100).toFixed(1);
    return {
      value: Math.abs(change),
      direction: change > 0 ? 'up' : change < 0 ? 'down' : 'stable'
    };
  };

  const getCurrentData = () => historicalData[selectedMetric][selectedPeriod] || [];
  const currentData = getCurrentData();
  const trend = calculateTrend(currentData);
  const average = currentData.length > 0 ? (currentData.reduce((a, b) => a + b, 0) / currentData.length).toFixed(1) : 0;
  const current = currentData[currentData.length - 1] || 0;

  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'up': return <TrendingUpIcon className="w-5 h-5 text-red-400" />;
      case 'down': return <TrendingDownIcon className="w-5 h-5 text-green-400" />;
      default: return <div className="w-5 h-5 flex items-center justify-center text-gray-400">→</div>;
    }
  };

  const getTrendColor = (direction) => {
    switch (direction) {
      case 'up': return selectedMetric === 'aqi' ? 'text-red-400' : 'text-green-400';
      case 'down': return selectedMetric === 'aqi' ? 'text-green-400' : 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="glass-card p-6">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold mb-2">Historical Data</h3>
            <p className="text-gray-400">Track environmental metrics over time</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-3">
            {/* Metric Selector */}
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="px-4 py-2 rounded-lg bg-dark-200 border border-gray-600 text-white focus:ring-2 focus:ring-primary-500"
            >
              <option value="aqi">Air Quality Index</option>
              <option value="temperature">Temperature</option>
              <option value="humidity">Humidity</option>
            </select>
            
            {/* Period Selector */}
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="px-4 py-2 rounded-lg bg-dark-200 border border-gray-600 text-white focus:ring-2 focus:ring-primary-500"
            >
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="1y">Last Year</option>
            </select>
          </div>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-card p-6 text-center">
          <h4 className="text-gray-400 text-sm font-medium mb-2">Current</h4>
          <div className="text-3xl font-bold text-white">{current}</div>
        </div>
        
        <div className="glass-card p-6 text-center">
          <h4 className="text-gray-400 text-sm font-medium mb-2">Average</h4>
          <div className="text-3xl font-bold text-blue-400">{average}</div>
        </div>
        
        <div className="glass-card p-6 text-center">
          <h4 className="text-gray-400 text-sm font-medium mb-2">Trend</h4>
          <div className={`text-3xl font-bold flex items-center justify-center gap-2 ${getTrendColor(trend.direction)}`}>
            {getTrendIcon(trend.direction)}
            {trend.value}%
          </div>
        </div>
        
        <div className="glass-card p-6 text-center">
          <h4 className="text-gray-400 text-sm font-medium mb-2">Best</h4>
          <div className="text-3xl font-bold text-green-400">
            {Math.min(...currentData).toFixed(0)}
          </div>
        </div>
      </div>

      {/* Chart Visualization */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
          <ChartBarIcon className="w-6 h-6 text-primary-400" />
          {getMetricLabel(selectedMetric)} - {selectedPeriod === '7d' ? 'Last 7 Days' : selectedPeriod === '30d' ? 'Last 30 Days' : 'Last Year'}
        </h3>
        
        {/* Simple Bar Chart */}
        <div className="relative h-64 flex items-end justify-between gap-1 p-4 bg-dark-300/50 rounded-xl">
          {currentData.slice(-20).map((value, index) => {
            const maxValue = Math.max(...currentData);
            const height = (value / maxValue) * 200;
            const color = selectedMetric === 'aqi' 
              ? (value <= 50 ? 'bg-green-400' : value <= 100 ? 'bg-yellow-400' : 'bg-red-400')
              : 'bg-primary-400';
            
            return (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div 
                  className={`w-full ${color} rounded-t transition-all hover:opacity-80`}
                  style={{ height: `${height}px` }}
                  title={`${value} ${selectedMetric === 'temperature' ? '°C' : selectedMetric === 'humidity' ? '%' : ''}`}
                ></div>
                <span className="text-xs text-gray-500 mt-2 transform -rotate-45">
                  {selectedPeriod === '7d' 
                    ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index % 7]
                    : `${index + 1}`
                  }
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Data Table */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
          <CalendarIcon className="w-6 h-6 text-primary-400" />
          Recent Readings
        </h3>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 font-medium text-gray-400">Date</th>
                <th className="text-left py-3 px-4 font-medium text-gray-400">Value</th>
                <th className="text-left py-3 px-4 font-medium text-gray-400">Status</th>
                <th className="text-left py-3 px-4 font-medium text-gray-400">Change</th>
              </tr>
            </thead>
            <tbody>
              {currentData.slice(-7).reverse().map((value, index) => {
                const prevValue = currentData[currentData.length - index - 2] || value;
                const change = value - prevValue;
                const changePercent = prevValue !== 0 ? ((change / prevValue) * 100).toFixed(1) : 0;
                
                return (
                  <tr key={index} className="border-b border-gray-800">
                    <td className="py-3 px-4 text-gray-300">
                      {new Date(Date.now() - index * 24 * 60 * 60 * 1000).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-white font-medium">
                      {value}{selectedMetric === 'temperature' ? '°C' : selectedMetric === 'humidity' ? '%' : ''}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        selectedMetric === 'aqi'
                          ? value <= 50 ? 'bg-green-500/20 text-green-400'
                            : value <= 100 ? 'bg-yellow-500/20 text-yellow-400'
                            : 'bg-red-500/20 text-red-400'
                          : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {selectedMetric === 'aqi'
                          ? value <= 50 ? 'Good' : value <= 100 ? 'Moderate' : 'Unhealthy'
                          : 'Normal'
                        }
                      </span>
                    </td>
                    <td className={`py-3 px-4 ${change > 0 ? 'text-red-400' : change < 0 ? 'text-green-400' : 'text-gray-400'}`}>
                      {change > 0 ? '+' : ''}{changePercent}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default HistoryTab;