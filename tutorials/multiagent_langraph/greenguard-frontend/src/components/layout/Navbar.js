import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Bars3Icon,
  BellIcon,
  MoonIcon,
  SunIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';
import { useNotification } from '../../context/NotificationContext';
import NotificationDropdown from '../common/NotificationDropdown';

const Navbar = ({ onMenuClick, theme, setTheme }) => {
  const { notifications, unreadCount } = useNotification();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <nav className="glass-card sticky top-0 z-50 border-b border-white/10">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left Section */}
          <div className="flex items-center gap-4">
            <button
              onClick={onMenuClick}
              className="lg:hidden p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              <Bars3Icon className="w-6 h-6" />
            </button>
            
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">G</span>
              </div>
              <h1 className="text-xl font-bold hidden sm:block">
                GreenGuard <span className="text-primary-400">v3.0</span>
              </h1>
            </Link>
          </div>

          {/* Center Section - Search */}
          <div className="hidden md:flex flex-1 max-w-xl mx-8">
            <div className="relative w-full">
              <input
                type="text"
                placeholder="Search cities, alerts, or ask a question..."
                className="w-full px-4 py-2 pl-10 bg-white/5 border border-white/10 rounded-xl 
                         focus:outline-none focus:border-primary-400 transition-all"
              />
              <svg className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-3">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? (
                <SunIcon className="w-6 h-6 text-yellow-400" />
              ) : (
                <MoonIcon className="w-6 h-6 text-gray-400" />
              )}
            </button>

            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 rounded-lg hover:bg-white/10 transition-colors relative"
              >
                <BellIcon className="w-6 h-6" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs 
                                 rounded-full flex items-center justify-center animate-pulse">
                    {unreadCount}
                  </span>
                )}
              </button>
              
              {showNotifications && (
                <NotificationDropdown
                  notifications={notifications}
                  onClose={() => setShowNotifications(false)}
                />
              )}
            </div>

            {/* Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowProfile(!showProfile)}
                className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <UserCircleIcon className="w-6 h-6" />
                <span className="hidden sm:block text-sm font-medium">Admin User</span>
              </button>
              
              {showProfile && (
                <div className="absolute right-0 mt-2 w-56 glass-card rounded-xl shadow-xl 
                               border border-white/10 animate-slide-up">
                  <div className="p-2">
                    <div className="px-3 py-2 border-b border-white/10">
                      <p className="text-sm font-medium">Admin User</p>
                      <p className="text-xs text-gray-400">admin@greenguard.ai</p>
                    </div>
                    
                    <Link
                      to="/settings"
                      className="menu-item mt-2"
                      onClick={() => setShowProfile(false)}
                    >
                      <Cog6ToothIcon className="w-5 h-5" />
                      <span>Settings</span>
                    </Link>
                    
                    <button className="menu-item w-full text-red-400 hover:bg-red-500/10">
                      <ArrowRightOnRectangleIcon className="w-5 h-5" />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;