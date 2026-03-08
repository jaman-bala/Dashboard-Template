import React from 'react';
import { X, AlertCircle, AlertTriangle, Info, XCircle } from 'lucide-react';

export interface ErrorModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  message: string;
  type?: 'error' | 'warning' | 'info';
  fieldErrors?: {
    [key: string]: string;
  };
}

export const ErrorModal: React.FC<ErrorModalProps> = ({
  isOpen,
  onClose,
  title = 'Ошибка',
  message,
  type = 'error',
  fieldErrors = {}
}) => {
  if (!isOpen) return null;

  const getIcon = () => {
    switch (type) {
      case 'error':
        return <XCircle className="w-6 h-6 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-6 h-6 text-yellow-500" />;
      case 'info':
        return <Info className="w-6 h-6 text-blue-500" />;
      default:
        return <AlertCircle className="w-6 h-6 text-red-500" />;
    }
  };

  const getBgColor = () => {
    switch (type) {
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'info':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-red-50 border-red-200';
    }
  };

  const getTextColor = () => {
    switch (type) {
      case 'error':
        return 'text-red-800';
      case 'warning':
        return 'text-yellow-800';
      case 'info':
        return 'text-blue-800';
      default:
        return 'text-red-800';
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md transform transition-all duration-300 ease-out">
        {/* Header */}
        <div className={`${getBgColor()} px-6 py-4 border-b rounded-t-2xl`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getIcon()}
              <h2 className={`text-lg font-semibold ${getTextColor()}`}>{title}</h2>
            </div>
            <button
              onClick={onClose}
              className={`p-2 ${getTextColor()} opacity-70 hover:opacity-100 
                       rounded-xl transition-all duration-200`}
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Main Error Message */}
          <div className={`mb-4 ${getTextColor()} leading-relaxed`}>
            {message}
          </div>

          {/* Field Errors */}
          {Object.keys(fieldErrors).length > 0 && (
            <div className="space-y-2">
              <div className={`text-sm font-medium ${getTextColor()}`}>Детали ошибок:</div>
              <div className="space-y-2">
                {Object.entries(fieldErrors).map(([field, error]) => (
                  <div key={field} className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-red-400 rounded-full mt-1.5 flex-shrink-0"></div>
                    <div>
                      <span className="text-sm font-medium text-gray-700 capitalize">
                        {field === 'email' ? 'Email' : field === 'phone' ? 'Телефон' : field}:
                      </span>
                      <span className="text-sm text-red-600 ml-1">{error}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Button */}
          <div className="mt-6 flex justify-end">
            <button
              onClick={onClose}
              className={`px-6 py-2 ${type === 'error' ? 'bg-red-500 hover:bg-red-600' : 
                              type === 'warning' ? 'bg-yellow-500 hover:bg-yellow-600' : 
                              'bg-blue-500 hover:bg-blue-600'} text-white rounded-xl 
                       font-medium transition-all duration-200 transform hover:scale-105`}
            >
              Понятно
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
