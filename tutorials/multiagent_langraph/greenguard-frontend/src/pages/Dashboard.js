import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ChartBarIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowTrendingUpIcon,
  MapPinIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import CityCard from '../components/dashboard/CityCard';
import MetricCard from '../components/dashboard/MetricCard';
import AlertsPanel from '../components/dashboard/AlertsPanel';
import WorldMap from '../components/dashboard/WorldMap';
import { useCity } from '../context/CityContext';
import api from '../services/api';

const Dashboard = () => {
  const { favorites, templateCities } = useCity();
  const [topCities, setTopCities] = useState([]);
  const [globalMetrics, setGlobalMetrics] = useState({
    totalAlerts: 0,
    criticalCities: 0,
    safeCities: 0,
    averageAQI: 0
  });
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState('overview');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Get top 5 cities data
      const cityPromises = templateCities.slice(0, 5).map(city => 
        api.checkCity(city.name)
      );
      
      const cityData = await Promise.all(cityPromises);
      
      // Calculate metrics
      const metrics = calculateGlobalMetrics(cityData);
      setGlobalMetrics(metrics);
      
      // Format top cities
      const formattedCities = cityData.map((data, index) => ({
        ...templateCities[index],
        ...data,
        aqi: data.hazard_data?.air_quality?.aqi || 45,
        status: getStatusFromAQI(data.hazard_data?.air_quality?.aqi || 45),
        alerts: Math.floor(Math.random() * 5) // Mock alerts count
      }));
      
      setTopCities(formattedCities);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateGlobalMetrics = (cityData) => {
    const aqiValues = cityData.map(d => d.hazard_data?.air_quality?.aqi || 45);
    const avgAQI = Math.round(aqiValues.reduce((a, b) => a + b, 0) / aqiValues.length);
    
    return {
      totalAlerts: cityData.reduce((sum, d) => sum + (d.alerts || 0), 0),
      criticalCities: aqiValues.filter(aqi => aqi > 100).length,
      safeCities: aqiValues.filter(aqi => aqi <= 50).length,
      averageAQI: avgAQI
    };
  };

  const getStatusFromAQI = (aqi) => {
    if (aqi <= 50) return 'good';
    if (aqi <= 100) return 'moderate';
    if (aqi <= 150) return 'unhealthy';
    return 'hazardous';
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: ChartBarIcon },
    { id: 'map', name: 'Global Map', icon: MapPinIcon },
    { id: 'alerts', name: 'Active Alerts', icon: ExclamationTriangleIcon },
    { id: 'trends', name: 'Trends', icon: ArrowTrendingUpIcon }
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="glass-card p-6">
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <SparklesIcon className="w-8 h-8 text-primary-400" />
              Environmental Health Dashboard
            </h1>
            <p className="text-gray-400 mt-2">
              Real-time monitoring of global environmental conditions
            </p>
          </div>
          <div className="flex gap-3">
            <button className="glass-button px-6 py-3 text-sm font-medium">
              Generate Report
            </button>
            <Link 
              to="/ai-insights" 
              className="gradient-primary text-white px-6 py-3 rounded-xl font-medium hover:shadow-lg transition-all"
            >
              AI Insights
            </Link>
          </div>
        </div>
      </div>

      {/* Global Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Active Alerts"
          value={globalMetrics.totalAlerts}
          icon={ExclamationTriangleIcon}
          trend="+12%"
          color="warning"
        />
        <MetricCard
          title="Critical Cities"
          value={globalMetrics.criticalCities}
          icon={ExclamationTriangleIcon}
          trend="-5%"
          color="danger"
        />
        <MetricCard
          title="Safe Cities"
          value={globalMetrics.safeCities}
          icon={CheckCircleIcon}
          trend="+8%"
          color="success"
        />
        <MetricCard
          title="Average AQI"
          value={globalMetrics.averageAQI}
          icon={ChartBarIcon}
          trend="+2%"
          color="primary"
        />
      </div>

      {/* Tab Navigation */}
      <div className="glass-card p-1">
        <nav className="flex space-x-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id)}
              className={`
                flex items-center gap-2 px-4 py-3 rounded-lg font-medium text-sm
                transition-all duration-200
                ${selectedTab === tab.id 
                  ? 'bg-primary-500/20 text-primary-400' 
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
                }
              `}
            >
              <tab.icon className="w-5 h-5" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="animate-fade-in">
        {selectedTab === 'overview' && (
          <>
            {/* Top 5 Cities */}
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <MapPinIcon className="w-6 h-6 text-primary-400" />
                Top 5 Monitored Cities
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
                {loading ? (
                  Array(5).fill(0).map((_, i) => (
                    <div key={i} className="glass-card p-6 h-48 shimmer" />
                  ))
                ) : (
                  topCities.map((city) => (
                    <CityCard key={city.id} city={city} />
                  ))
                )}
              </div>
            </div>

            {/* Recent Alerts */}
            <AlertsPanel cities={topCities} />
          </>
        )}

        {selectedTab === 'map' && (
          <div className="glass-card p-6">
            <WorldMap cities={topCities} />
          </div>
        )}

        {selectedTab === 'alerts' && (
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">All Active Alerts</h3>
            <AlertsPanel cities={topCities} showAll={true} />
          </div>
        )}

        {selectedTab === 'trends' && (
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">Environmental Trends</h3>
            <p className="text-gray-400">Trend analysis coming soon...</p>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link 
            to="/ai-insights"
            className="glass-button p-4 text-center hover:border-primary-400 transition-all"
          >
            <SparklesIcon className="w-8 h-8 mx-auto mb-2 text-primary-400" />
            <p className="font-medium">Ask AI Assistant</p>
            <p className="text-sm text-gray-400 mt-1">Get environmental insights</p>
          </Link>
          <button className="glass-button p-4 text-center hover:border-secondary-400 transition-all">
            <ChartBarIcon className="w-8 h-8 mx-auto mb-2 text-secondary-400" />
            <p className="font-medium">View Analytics</p>
            <p className="text-sm text-gray-400 mt-1">Detailed statistics</p>
          </button>
          <button className="glass-button p-4 text-center hover:border-green-400 transition-all">
            <MapPinIcon className="w-8 h-8 mx-auto mb-2 text-green-400" />
            <p className="font-medium">Add City</p>
            <p className="text-sm text-gray-400 mt-1">Monitor new location</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;