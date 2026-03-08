import React, { useState, useEffect } from 'react';
import { X, Upload, User as UserIcon } from 'lucide-react';
import { User, UserFormData } from '../types/User';
import { roleLabels } from '../utils/mockData';

interface UserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (userData: UserFormData) => void;
  user?: User | null;
  mode: 'add' | 'edit' | 'view';
  fieldErrors?: {
    email?: string;
    phone?: string;
  };
}

export const UserModal: React.FC<UserModalProps> = ({
  isOpen,
  onClose,
  onSave,
  user,
  mode,
  fieldErrors = {}
}) => {
  const [formData, setFormData] = useState<UserFormData>({
    first_name: '',
    last_name: '',
    middle_name: '',
    email: '',
    phone: '',
    roles: ['USER'],
    is_active: true,
    password: ''
  });

  const [avatar, setAvatar] = useState<string>('');
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        middle_name: user.middle_name || '',
        email: user.email || '',
        phone: user.phone,
        roles: user.roles || ['USER'],
        is_active: user.is_active
      });
      setAvatar(user.photo || '');
    } else {
      setFormData({
        first_name: '',
        last_name: '',
        middle_name: '',
        email: '',
        phone: '',
        roles: ['USER'],
        is_active: true,
        password: ''
      });
      setAvatar('');
    }
  }, [user]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
    setFormData({
      first_name: '',
      last_name: '',
      middle_name: '',
      email: '',
      phone: '',
      roles: ['USER'],
      is_active: true,
      password: ''
    });
    setAvatar('');
    onClose();
  };

  const handleInputChange = (field: keyof UserFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Сохраняем файл в formData
      setFormData(prev => ({ ...prev, photo: file }));

      // Создаем preview для отображения
      const reader = new FileReader();
      reader.onload = (e) => {
        setAvatar(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  if (!isOpen) return null;

  const isReadonly = mode === 'view';
  const title = mode === 'add' ? 'Добавить пользователя' :
                mode === 'edit' ? 'Редактировать пользователя' :
                'Информация о пользователе';

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden
                    transform transition-all duration-300 ease-out">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">{title}</h2>
            <button
              onClick={onClose}
              className="p-2 text-white/80 hover:text-white hover:bg-white/10
                       rounded-xl transition-all duration-200"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Avatar Section */}
            <div className="text-center">
              <div className="relative inline-block">
                <div className="w-24 h-24 rounded-full overflow-hidden bg-gray-100 border-4 border-white shadow-lg">
                  {avatar ? (
                    <img src={avatar} alt="Avatar" className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
                      <UserIcon className="w-8 h-8 text-gray-400" />
                    </div>
                  )}
                </div>
                {!isReadonly && (
                  <label className="absolute bottom-0 right-0 bg-blue-500 hover:bg-blue-600
                                 text-white rounded-full p-2 cursor-pointer shadow-lg
                                 transition-all duration-200 transform hover:scale-105">
                    <Upload className="w-4 h-4" />
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarChange}
                      className="hidden"
                    />
                  </label>
                )}
              </div>
            </div>

            {/* Form Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Имя *
                </label>
                <input
                  type="text"
                  required
                  disabled={isReadonly}
                  value={formData.first_name || ''}
                  onChange={(e) => handleInputChange('first_name', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:bg-gray-50 disabled:text-gray-500
                           transition-all duration-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Фамилия *
                </label>
                <input
                  type="text"
                  required
                  disabled={isReadonly}
                  value={formData.last_name || ''}
                  onChange={(e) => handleInputChange('last_name', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:bg-gray-50 disabled:text-gray-500
                           transition-all duration-200"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Отчество
                </label>
                <input
                  type="text"
                  disabled={isReadonly}
                  value={formData.middle_name || ''}
                  onChange={(e) => handleInputChange('middle_name', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:bg-gray-50 disabled:text-gray-500
                           transition-all duration-200"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  disabled={isReadonly}
                  value={formData.email || ''}
                  onChange={(e) => {
                    handleInputChange('email', e.target.value);
                  }}
                  className={`w-full px-4 py-3 border rounded-xl
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:bg-gray-50 disabled:text-gray-500
                           transition-all duration-200
                           ${fieldErrors.email ? 'border-red-500 focus:ring-red-500' : 'border-gray-200'}`}
                />
                {fieldErrors.email && (
                  <p className="mt-1 text-sm text-red-600">{fieldErrors.email}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Телефон *
                </label>
                <input
                  type="tel"
                  required
                  disabled={isReadonly}
                  value={formData.phone || ''}
                  onChange={(e) => {
                    handleInputChange('phone', e.target.value);
                  }}
                  className={`w-full px-4 py-3 border rounded-xl
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:bg-gray-50 disabled:text-gray-500
                           transition-all duration-200
                           ${fieldErrors.phone ? 'border-red-500 focus:ring-red-500' : 'border-gray-200'}`}
                />
                {fieldErrors.phone && (
                  <p className="mt-1 text-sm text-red-600">{fieldErrors.phone}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Роль
                </label>
                <select
                  disabled={isReadonly}
                  value={formData.roles?.[0] || 'USER'}
                  onChange={(e) => handleInputChange('roles', [e.target.value])}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl
                           focus:ring-2 focus:ring-blue-500 focus:border-transparent
                           disabled:bg-gray-50 disabled:text-gray-500
                           transition-all duration-200"
                >
                  {Object.entries(roleLabels).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    disabled={isReadonly}
                    checked={formData.is_active}
                    onChange={(e) => handleInputChange('is_active', e.target.checked)}
                    className="sr-only"
                  />
                  <div className={`relative w-11 h-6 rounded-full transition-colors duration-200
                                 ${formData.is_active ? 'bg-blue-500' : 'bg-gray-300'}`}>
                    <div className={`absolute left-1 top-1 w-4 h-4 bg-white rounded-full
                                   transition-transform duration-200
                                   ${formData.is_active ? 'translate-x-5' : 'translate-x-0'}`} />
                  </div>
                  <span className="ml-3 text-sm font-medium text-gray-700">
                    Активен
                  </span>
                </label>
              </div>

              {(mode === 'add' || mode === 'edit') && (
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {mode === 'add' ? 'Пароль *' : 'Новый пароль (оставьте пустым, если не меняется)'}
                  </label>
                  <div className="relative">
                    <input
                      type={showPassword ? "text" : "password"}
                      required={mode === 'add'}
                      value={formData.password || ''}
                      onChange={(e) => handleInputChange('password', e.target.value)}
                      className="w-full px-4 py-3 pr-12 border border-gray-200 rounded-xl
                               focus:ring-2 focus:ring-blue-500 focus:border-transparent
                               transition-all duration-200"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    >
                      {showPassword ? (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            {!isReadonly && (
              <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-6 py-3 text-gray-700 bg-gray-100 hover:bg-gray-200
                           rounded-xl font-medium transition-all duration-200
                           transform hover:scale-105"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500
                           hover:from-blue-600 hover:to-purple-600 text-white rounded-xl
                           font-medium transition-all duration-200 transform hover:scale-105
                           shadow-lg hover:shadow-xl"
                >
                  {mode === 'add' ? 'Создать' : 'Сохранить'}
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};
