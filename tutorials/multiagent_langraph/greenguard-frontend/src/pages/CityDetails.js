import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  MapPinIcon,
  CloudIcon,
  BeakerIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  ClockIcon,
  HeartIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';
import AirQualityTab from '../components/city/AirQualityTab';
import WaterQualityTab from '../components/city/WaterQualityTab';
import WeatherTab from '../components/city/WeatherTab';
import AlertsTab from '../components/city/AlertsTab';
import HistoryTab from '../components/city/HistoryTab';
import { useCity } from '../context/CityContext';
import api from '../services/api';

const CityDetails = () => {
  const { cityId } = useParams();
  const navigate = useNavigate();
  const { templateCities, favorites, toggleFavorite } = useCity();
  const [selectedTab, setSelectedTab] = useState('air');
  const [cityData, setCityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const city = templateCities.find(c => c.id === cityId);
  const isFavorite = favorites.includes(city?.name);

  useEffect(() => {
    if (city) {
      fetchCityData();
    }
  }, [city]);

  const fetchCityData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.checkCity(city.name);
      setCityData(response);
    } catch (err) {
      setError('Failed to fetch city data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'air', name: 'Air Quality', icon: CloudIcon, color: 'blue' },
    { id: 'water', name: 'Water Quality', icon: BeakerIcon, color: 'cyan' },
    { id: 'weather', name: 'Weather', icon: CloudIcon, color: 'purple' },
    { id: 'alerts', name: 'Alerts', icon: ExclamationTriangleIcon, color: 'red' },
    { id: 'history', name: 'History', icon: ClockIcon, color: 'gray' }
  ];

  const getAQIStatus = (aqi = 45) => {
    if (aqi <= 50) return { text: 'Good', color: 'text-green-400', bg: 'bg-green-500/20' };
    if (aqi <= 100) return { text: 'Moderate', color: 'text-yellow-400', bg: 'bg-yellow-500/20' };
    if (aqi <= 150) return { text: 'Unhealthy', color: 'text-orange-400', bg: 'bg-orange-500/20' };
    return { text: 'Hazardous', color: 'text-red-400', bg: 'bg-red-500/20' };
  };

  if (!city) {
    return (
      <div className="glass-card p-8 text-center">
        <p className="text-gray-400">City not found</p>
        <button
          onClick={() => navigate('/')}
          className="mt-4 glass-button px-6 py-2"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  const aqi = cityData?.hazard_data?.air_quality?.aqi || 45;
  const aqiStatus = getAQIStatus(aqi);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeftIcon className="w-5 h-5" />
            <span>Back</span>
          </button>
          
          <button
            onClick={() => toggleFavorite(city.name)}
            className="flex items-center gap-2 glass-button px-4 py-2"
          >
            {isFavorite ? (
              <HeartSolidIcon className="w-5 h-5 text-yellow-400" />
            ) : (
              <HeartIcon className="w-5 h-5" />
            )}
            <span>{isFavorite ? 'Favorited' : 'Add to Favorites'}</span>
          </button>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* City Info */}
          <div className="flex-1">
            <div className="flex items-start gap-4">
              <div className="text-5xl">{city.icon}</div>
              <div>
                <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                  {city.name}
                  <MapPinIcon className="w-6 h-6 text-gray-400" />
                </h1>
                <p className="text-gray-400 mt-1">
                  Coordinates: {city.coordinates.lat}°, {city.coordinates.lon}°
                </p>
                <div className="flex flex-wrap gap-2 mt-3">
                  {city.common_hazards.map((hazard) => (
                    <span
                      key={hazard}
                      className="px-3 py-1 text-xs rounded-full bg-orange-500/20 text-orange-400"
                    >
                      {hazard.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Current Status */}
          <div className="lg:w-80">
            <div className={`${aqiStatus.bg} rounded-2xl p-6 text-center`}>
              <p className="text-sm text-gray-300 mb-2">Current AQI</p>
              <p className={`text-5xl font-bold ${aqiStatus.color}`}>{aqi}</p>
              <p className={`text-lg font-medium mt-2 ${aqiStatus.color}`}>
                {aqiStatus.text}
              </p>
              <p className="text-sm text-gray-400 mt-4">
                Last updated: {new Date().toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="glass-card p-1">
        <nav className="flex space-x-1 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedTab(tab.id)}
              className={`
                flex items-center gap-2 px-4 py-3 rounded-lg font-medium text-sm
                transition-all duration-200 whitespace-nowrap
                ${selectedTab === tab.id 
                  ? `bg-${tab.color}-500/20 text-${tab.color}-400` 
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
        {loading ? (
          <div className="glass-card p-8 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary-400 border-t-transparent"></div>
            <p className="mt-4 text-gray-400">Loading city data...</p>
          </div>
        ) : error ? (
          <div className="glass-card p-8 text-center">
            <ExclamationTriangleIcon className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <p className="text-red-400">{error}</p>
            <button onClick={fetchCityData} className="mt-4 glass-button px-6 py-2">
              Retry
            </button>
          </div>
        ) : (
          <>
            {selectedTab === 'air' && <AirQualityTab data={cityData} city={city} />}
            {selectedTab === 'water' && <WaterQualityTab data={cityData} city={city} />}
            {selectedTab === 'weather' && <WeatherTab data={cityData} city={city} />}
            {selectedTab === 'alerts' && <AlertsTab data={cityData} city={city} />}
            {selectedTab === 'history' && <HistoryTab city={city} />}
          </>
        )}
      </div>

      {/* Quick Actions */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-3">
          <button className="glass-button px-4 py-2 text-sm">
            Download Report
          </button>
          <button className="glass-button px-4 py-2 text-sm">
            Set Alert Threshold
          </button>
          <button className="glass-button px-4 py-2 text-sm">
            Share Dashboard
          </button>
          <button className="gradient-primary text-white px-4 py-2 rounded-lg text-sm">
            Get AI Analysis
          </button>
        </div>
      </div>
    </div>
  );
};

export default CityDetails;