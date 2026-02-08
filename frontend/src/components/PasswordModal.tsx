import React, { useState } from 'react';
import { X, Eye, EyeOff, Lock } from 'lucide-react';

interface PasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (passwords: { new: string; confirm: string }) => void;
  userName: string;
}

export const PasswordModal: React.FC<PasswordModalProps> = ({
  isOpen,
  onClose,
  onSave,
  userName
}) => {
  const [passwords, setPasswords] = useState({
    new: '',
    confirm: ''
  });
  
  const [showPasswords, setShowPasswords] = useState({
    new: false,
    confirm: false
  });

  const [errors, setErrors] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const newErrors: string[] = [];
    
    if (passwords.new.length < 6) {
      newErrors.push('Новый пароль должен содержать минимум 6 символов');
    }
    
    if (passwords.new !== passwords.confirm) {
      newErrors.push('Пароли не совпадают');
    }
    

    setErrors(newErrors);

    if (newErrors.length === 0) {
      onSave(passwords);
      handleClose();
    }
  };

  const handleClose = () => {
    setPasswords({ new: '', confirm: '' });
    setErrors([]);
    setShowPasswords({ new: false, confirm: false });
    onClose();
  };

  const togglePasswordVisibility = (field: keyof typeof showPasswords) => {
    setShowPasswords(prev => ({ ...prev, [field]: !prev[field] }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md transform transition-all duration-300 ease-out">
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-500 to-red-500 px-6 py-4 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                <Lock className="w-4 h-4 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Смена пароля</h2>
                <p className="text-white/80 text-sm">{userName}</p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="p-2 text-white/80 hover:text-white hover:bg-white/10 
                       rounded-xl transition-all duration-200"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {errors.length > 0 && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl">
              <div className="text-sm text-red-600">
                {errors.map((error, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div className="w-1 h-1 bg-red-400 rounded-full"></div>
                    <span>{error}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* New Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Новый пароль
              </label>
              <div className="relative">
                <input
                  type={showPasswords.new ? 'text' : 'password'}
                  required
                  value={passwords.new}
                  onChange={(e) => setPasswords(prev => ({ ...prev, new: e.target.value }))}
                  className="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl
                           focus:ring-2 focus:ring-orange-500 focus:border-transparent
                           transition-all duration-200"
                  placeholder="Введите новый пароль"
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('new')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center
                           text-gray-400 hover:text-gray-600 transition-colors duration-150"
                >
                  {showPasswords.new ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Подтверждение пароля
              </label>
              <div className="relative">
                <input
                  type={showPasswords.confirm ? 'text' : 'password'}
                  required
                  value={passwords.confirm}
                  onChange={(e) => setPasswords(prev => ({ ...prev, confirm: e.target.value }))}
                  className="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl
                           focus:ring-2 focus:ring-orange-500 focus:border-transparent
                           transition-all duration-200"
                  placeholder="Повторите новый пароль"
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('confirm')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center
                           text-gray-400 hover:text-gray-600 transition-colors duration-150"
                >
                  {showPasswords.confirm ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-4 pt-4">
              <button
                type="button"
                onClick={handleClose}
                className="px-6 py-3 text-gray-700 bg-gray-100 hover:bg-gray-200
                         rounded-xl font-medium transition-all duration-200
                         transform hover:scale-105"
              >
                Отмена
              </button>
              <button
                type="submit"
                className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500
                         hover:from-orange-600 hover:to-red-600 text-white rounded-xl
                         font-medium transition-all duration-200 transform hover:scale-105
                         shadow-lg hover:shadow-xl"
              >
                Изменить пароль
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};