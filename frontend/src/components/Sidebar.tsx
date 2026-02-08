import React, { useState } from 'react';
import { 
  Users, 
  Settings, 
  BarChart3, 
  Shield, 
  Bell, 
  HelpCircle, 
  LogOut,
  ChevronLeft,
  ChevronRight,
  Home,
  UserCog,
  Database,
  Activity
} from 'lucide-react';

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
  activeItem: string;
  onItemClick: (item: string) => void;
}

const menuItems = [
  { id: 'dashboard', label: 'Главная', icon: Home },
  { id: 'users', label: 'Пользователи', icon: Users },
  { id: 'analytics', label: 'Аналитика', icon: BarChart3 },
  { id: 'roles', label: 'Роли и права', icon: Shield },
  { id: 'activity', label: 'Активность', icon: Activity },
  { id: 'database', label: 'База данных', icon: Database },
];

const bottomItems = [
  { id: 'notifications', label: 'Уведомления', icon: Bell },
  { id: 'settings', label: 'Настройки', icon: Settings },
  { id: 'help', label: 'Помощь', icon: HelpCircle },
];

export const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed,
  onToggle,
  activeItem,
  onItemClick
}) => {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const MenuItem = ({ item, isBottom = false }: { item: any; isBottom?: boolean }) => {
    const Icon = item.icon;
    const isActive = activeItem === item.id;
    const isHovered = hoveredItem === item.id;

    return (
      <button
        onClick={() => onItemClick(item.id)}
        onMouseEnter={() => setHoveredItem(item.id)}
        onMouseLeave={() => setHoveredItem(null)}
        className={`
          w-full flex items-center px-3 py-3 rounded-xl text-left
          transition-all duration-300 ease-out group relative
          ${isActive 
            ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg transform scale-105' 
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }
          ${isCollapsed ? 'justify-center' : 'justify-start'}
        `}
      >
        <div className={`
          flex items-center justify-center w-6 h-6 
          transition-transform duration-300
          ${isActive ? 'scale-110' : isHovered ? 'scale-105' : 'scale-100'}
        `}>
          <Icon className="w-5 h-5" />
        </div>
        
        <span className={`
          ml-3 font-medium transition-all duration-300
          ${isCollapsed ? 'opacity-0 w-0' : 'opacity-100 w-auto'}
        `}>
          {item.label}
        </span>

        {/* Active indicator */}
        {isActive && (
          <div className="absolute right-2 w-2 h-2 bg-white rounded-full opacity-80" />
        )}

        {/* Tooltip for collapsed state */}
        {isCollapsed && isHovered && (
          <div className="absolute left-full ml-2 px-3 py-2 bg-gray-900 text-white text-sm 
                         rounded-lg shadow-lg z-50 whitespace-nowrap
                         transform transition-all duration-200 ease-out">
            {item.label}
            <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 
                           w-2 h-2 bg-gray-900 rotate-45" />
          </div>
        )}
      </button>
    );
  };

  return (
    <div className={`
      fixed left-0 top-0 h-full bg-white border-r border-gray-200 shadow-xl z-40
      transition-all duration-300 ease-out
      ${isCollapsed ? 'w-20' : 'w-72'}
    `}>
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-100">
        <div className={`
          flex items-center space-x-3 transition-all duration-300
          ${isCollapsed ? 'opacity-0 w-0' : 'opacity-100 w-auto'}
        `}>
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 
                         rounded-xl flex items-center justify-center shadow-lg">
            <UserCog className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">UserPanel</h1>
            <p className="text-xs text-gray-500">Admin Dashboard</p>
          </div>
        </div>
        
        <button
          onClick={onToggle}
          className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 
                   rounded-lg transition-all duration-200 transform hover:scale-105"
        >
          {isCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>

      {/* Navigation */}
      <div className="flex flex-col h-full">
        {/* Main Menu */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {menuItems.map((item) => (
            <MenuItem key={item.id} item={item} />
          ))}
        </nav>

        {/* Bottom Menu */}
        <div className="px-4 py-6 border-t border-gray-100 space-y-2">
          {bottomItems.map((item) => (
            <MenuItem key={item.id} item={item} isBottom />
          ))}
          
          {/* Logout Button */}
          <button
            className={`
              w-full flex items-center px-3 py-3 rounded-xl text-left
              text-red-600 hover:text-red-700 hover:bg-red-50
              transition-all duration-300 ease-out group
              ${isCollapsed ? 'justify-center' : 'justify-start'}
            `}
          >
            <LogOut className="w-5 h-5" />
            <span className={`
              ml-3 font-medium transition-all duration-300
              ${isCollapsed ? 'opacity-0 w-0' : 'opacity-100 w-auto'}
            `}>
              Выйти
            </span>
          </button>
        </div>

        {/* User Profile */}
        <div className={`
          p-4 border-t border-gray-100 bg-gradient-to-r from-gray-50 to-blue-50/30
          transition-all duration-300
          ${isCollapsed ? 'px-2' : 'px-4'}
        `}>
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full overflow-hidden bg-gradient-to-br from-blue-400 to-purple-500 
                           shadow-md ring-2 ring-white flex-shrink-0">
              <img 
                src="https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg?auto=compress&cs=tinysrgb&w=150" 
                alt="Admin" 
                className="w-full h-full object-cover" 
              />
            </div>
            <div className={`
              transition-all duration-300 min-w-0
              ${isCollapsed ? 'opacity-0 w-0' : 'opacity-100 w-auto'}
            `}>
              <p className="text-sm font-semibold text-gray-900 truncate">Александр Иванов</p>
              <p className="text-xs text-gray-500 truncate">Администратор</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};