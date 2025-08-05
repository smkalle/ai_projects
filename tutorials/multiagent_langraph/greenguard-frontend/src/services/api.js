import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add session ID to all requests
api.interceptors.request.use((config) => {
  const sessionId = localStorage.getItem('greenguard_session') || generateSessionId();
  config.headers['session-id'] = sessionId;
  return config;
});

// Generate session ID
function generateSessionId() {
  const id = 'session_' + Math.random().toString(36).substr(2, 9);
  localStorage.setItem('greenguard_session', id);
  return id;
}

// API Methods
const apiService = {
  // Template Cities
  async getTemplateCities() {
    const response = await api.get('/api/template-cities');
    return response.data;
  },

  // Favorites
  async getFavorites() {
    const response = await api.get('/api/favorites');
    return response.data;
  },

  async addFavorite(city) {
    const response = await api.post('/api/favorites', { city });
    return response.data;
  },

  async removeFavorite(city) {
    const response = await api.delete(`/api/favorites/${encodeURIComponent(city)}`);
    return response.data;
  },

  // AI Insights
  async getAIInsights(query, location) {
    const response = await api.post('/api/ai-insights', { query, location });
    return response.data;
  },

  // City Monitoring
  async checkCity(location) {
    const response = await api.post('/trigger-check', { location });
    return response.data;
  },

  // WebSocket Connection
  connectWebSocket(onMessage) {
    const ws = new WebSocket(`ws://localhost:8000/ws`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Reconnect after 3 seconds
      setTimeout(() => this.connectWebSocket(onMessage), 3000);
    };
    
    return ws;
  },
};

export default apiService;