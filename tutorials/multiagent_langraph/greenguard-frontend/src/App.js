import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './pages/Dashboard';
import CityDetails from './pages/CityDetails';
import AIInsights from './pages/AIInsights';
import Settings from './pages/Settings';
import { CityProvider } from './context/CityContext';
import { NotificationProvider } from './context/NotificationContext';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    // Apply theme
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  return (
    <Router>
      <CityProvider>
        <NotificationProvider>
          <div className="min-h-screen bg-gradient-to-br from-dark-300 via-dark-200 to-dark-300">
            {/* Background Pattern */}
            <div className="fixed inset-0 opacity-10">
              <div className="absolute inset-0" style={{
                backgroundImage: `radial-gradient(circle at 1px 1px, white 1px, transparent 1px)`,
                backgroundSize: '40px 40px'
              }}></div>
            </div>

            {/* Main Layout */}
            <div className="relative z-10">
              <Navbar 
                onMenuClick={() => setSidebarOpen(!sidebarOpen)} 
                theme={theme}
                setTheme={setTheme}
              />
              
              <div className="flex">
                <Sidebar 
                  isOpen={sidebarOpen} 
                  onClose={() => setSidebarOpen(false)} 
                />
                
                <main className="flex-1 p-6 lg:ml-64">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/city/:cityId" element={<CityDetails />} />
                    <Route path="/ai-insights" element={<AIInsights />} />
                    <Route path="/settings" element={<Settings />} />
                  </Routes>
                </main>
              </div>
            </div>
          </div>
        </NotificationProvider>
      </CityProvider>
    </Router>
  );
}

export default App;