import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const CityContext = createContext();

export const useCity = () => {
  const context = useContext(CityContext);
  if (!context) {
    throw new Error('useCity must be used within a CityProvider');
  }
  return context;
};

export const CityProvider = ({ children }) => {
  const [templateCities, setTemplateCities] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      
      // Fetch template cities
      const citiesData = await api.getTemplateCities();
      setTemplateCities(citiesData.cities || []);
      
      // Fetch favorites
      const favoritesData = await api.getFavorites();
      setFavorites(favoritesData.favorites || []);
      
    } catch (error) {
      console.error('Failed to fetch initial data:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleFavorite = async (cityName) => {
    try {
      if (favorites.includes(cityName)) {
        // Remove favorite
        const response = await api.removeFavorite(cityName);
        setFavorites(response.favorites);
      } else {
        // Add favorite
        if (favorites.length >= 5) {
          throw new Error('Maximum 5 favorite cities allowed');
        }
        const response = await api.addFavorite(cityName);
        setFavorites(response.favorites);
      }
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
      throw error;
    }
  };

  const getCityById = (cityId) => {
    return templateCities.find(city => city.id === cityId);
  };

  const isFavorite = (cityName) => {
    return favorites.includes(cityName);
  };

  const value = {
    templateCities,
    favorites,
    loading,
    toggleFavorite,
    getCityById,
    isFavorite,
    refreshData: fetchInitialData
  };

  return (
    <CityContext.Provider value={value}>
      {children}
    </CityContext.Provider>
  );
};