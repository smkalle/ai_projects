import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  GlobeAmericasIcon,
  SparklesIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  BookOpenIcon,
  HeartIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const Sidebar = ({ isOpen, onClose }) => {
  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'City Monitor', href: '/cities', icon: GlobeAmericasIcon },
    { name: 'AI Insights', href: '/ai-insights', icon: SparklesIcon },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
  ];

  const favorites = [
    { name: 'New York', href: '/city/nyc', emoji: '🗽' },
    { name: 'Tokyo', href: '/city/tokyo', emoji: '🗼' },
    { name: 'London', href: '/city/london', emoji: '🏰' },
  ];

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 z-40 h-full w-64 
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:static lg:z-30
        `}
      >
        <div className="h-full glass-card border-r border-white/10 flex flex-col">
          {/* Mobile close button */}
          <div className="lg:hidden flex justify-end p-4">
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-white/10 transition-colors"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 pb-4 space-y-1">
            <div className="mb-8">
              <h3 className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                Main Menu
              </h3>
              {navigation.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  className={({ isActive }) =>
                    `menu-item ${
                      isActive
                        ? 'bg-primary-500/20 text-primary-400 border-l-4 border-primary-400'
                        : 'text-gray-300 hover:text-white'
                    }`
                  }
                  onClick={() => onClose()}
                >
                  <item.icon className="w-6 h-6" />
                  <span className="font-medium">{item.name}</span>
                </NavLink>
              ))}
            </div>

            {/* Favorites Section */}
            <div>
              <h3 className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <HeartIcon className="w-4 h-4" />
                Favorite Cities
              </h3>
              {favorites.map((city) => (
                <NavLink
                  key={city.name}
                  to={city.href}
                  className={({ isActive }) =>
                    `menu-item ${
                      isActive
                        ? 'bg-yellow-500/20 text-yellow-400'
                        : 'text-gray-300 hover:text-white'
                    }`
                  }
                  onClick={() => onClose()}
                >
                  <span className="text-2xl">{city.emoji}</span>
                  <span className="font-medium">{city.name}</span>
                </NavLink>
              ))}
            </div>
          </nav>

          {/* Bottom Section */}
          <div className="p-4 border-t border-white/10">
            <div className="glass-card p-4 text-center">
              <BookOpenIcon className="w-8 h-8 mx-auto mb-2 text-primary-400" />
              <h4 className="text-sm font-semibold mb-1">Need Help?</h4>
              <p className="text-xs text-gray-400 mb-3">
                Check our documentation
              </p>
              <button className="w-full glass-button py-2 text-sm">
                View Docs
              </button>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;