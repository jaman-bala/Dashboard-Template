import React from 'react';
import { Search, X } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  placeholder = "Поиск по имени или телефону..."
}) => {
  return (
    <div className="relative">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <Search className="h-5 w-5 text-gray-400" />
      </div>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="block w-full pl-10 pr-10 py-3 border border-gray-200 rounded-xl 
                 bg-white/50 backdrop-blur-sm
                 focus:ring-2 focus:ring-blue-500 focus:border-transparent
                 transition-all duration-200 ease-in-out
                 placeholder-gray-400 text-gray-900"
        placeholder={placeholder}
      />
      {value && (
        <button
          onClick={() => onChange('')}
          className="absolute inset-y-0 right-0 pr-3 flex items-center
                   text-gray-400 hover:text-gray-600 transition-colors duration-150"
        >
          <X className="h-5 w-5" />
        </button>
      )}
    </div>
  );
};