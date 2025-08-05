import React from 'react';

const MetricCard = ({ title, value, icon: Icon, trend, color = 'primary' }) => {
  const getColorClasses = (color) => {
    const colors = {
      primary: 'text-primary-400 bg-primary-500/20',
      success: 'text-green-400 bg-green-500/20',
      warning: 'text-yellow-400 bg-yellow-500/20',
      danger: 'text-red-400 bg-red-500/20'
    };
    return colors[color] || colors.primary;
  };

  const getTrendColor = (trend) => {
    if (!trend) return 'text-gray-400';
    return trend.startsWith('+') ? 'text-green-400' : 'text-red-400';
  };

  return (
    <div className="metric-card">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold text-white mt-2">{value}</p>
          {trend && (
            <p className={`text-sm mt-2 ${getTrendColor(trend)}`}>
              {trend} from last week
            </p>
          )}
        </div>
        <div className={`p-3 rounded-xl ${getColorClasses(color)}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
};

export default MetricCard;