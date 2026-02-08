import React from 'react';
import { Eye, Edit, Trash2, Key, UserX, UserCheck, Phone, Mail, Clock } from 'lucide-react';
import { UserDisplay } from '../types/User';
import { roleLabels, roleColors } from '../utils/mockData';

interface UserTableProps {
  users: UserDisplay[];
  onView: (user: UserDisplay) => void;
  onEdit: (user: UserDisplay) => void;
  onDelete: (user: UserDisplay) => void;
  onChangePassword: (user: UserDisplay) => void;
  onToggleStatus: (user: UserDisplay) => void;
}

export const UserTable: React.FC<UserTableProps> = ({
  users,
  onView,
  onEdit,
  onDelete,
  onChangePassword,
  onToggleStatus
}) => {
  const formatLastLogin = (date?: Date) => {
    if (!date) return 'Никогда';
    
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMinutes < 1) return 'Только что';
    if (diffMinutes < 60) return `${diffMinutes} мин назад`;
    if (diffHours < 24) return `${diffHours} ч назад`;
    if (diffDays < 7) return `${diffDays} дн назад`;
    
    return date.toLocaleDateString('ru-RU');
  };

  if (users.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
        <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <UserX className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Пользователи не найдены</h3>
        <p className="text-gray-500">Попробуйте изменить параметры поиска</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200">
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Пользователь
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Контакты
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Роль
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Статус
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Последний вход
              </th>
              <th className="px-6 py-4 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {users.map((user) => (
              <tr key={user.id} 
                  className="group hover:bg-gradient-to-r hover:from-blue-50/50 hover:to-purple-50/50 
                           transition-all duration-200">
                {/* User Info */}
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 rounded-full overflow-hidden bg-gradient-to-br from-blue-400 to-purple-500 
                                    shadow-md ring-2 ring-white">
                        {user.avatar ? (
                          <img src={user.avatar} alt="Avatar" className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-white font-semibold">
                            {user.firstName[0]}{user.lastName[0]}
                          </div>
                        )}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-gray-900">
                        {user.lastName} {user.firstName} {user.middleName}
                      </div>
                      <div className="text-xs text-gray-500">
                        ID: {user.id}
                      </div>
                    </div>
                  </div>
                </td>

                {/* Contacts */}
                <td className="px-6 py-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2 text-sm text-gray-900">
                      <Phone className="w-4 h-4 text-gray-400" />
                      <span className="font-medium">{user.phone}</span>
                    </div>
                    {user.email && (
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <Mail className="w-4 h-4 text-gray-400" />
                        <span>{user.email}</span>
                      </div>
                    )}
                  </div>
                </td>

                {/* Role */}
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border
                                 ${roleColors[user.role]}`}>
                    {roleLabels[user.role]}
                  </span>
                </td>

                {/* Status */}
                <td className="px-6 py-4">
                  <button
                    onClick={() => onToggleStatus(user)}
                    className="group flex items-center space-x-2"
                  >
                    <div className={`w-2 h-2 rounded-full transition-colors duration-200
                                   ${user.isActive ? 'bg-green-400' : 'bg-gray-400'}`} />
                    <span className={`text-xs font-medium transition-colors duration-200
                                    ${user.isActive ? 'text-green-600' : 'text-gray-500'}`}>
                      {user.isActive ? 'Активен' : 'Неактивен'}
                    </span>
                    {user.isActive ? 
                      <UserCheck className="w-3 h-3 text-green-400 opacity-0 group-hover:opacity-100 transition-opacity" /> :
                      <UserX className="w-3 h-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                    }
                  </button>
                </td>

                {/* Last Login */}
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <Clock className="w-4 h-4 text-gray-400" />
                    <span>{formatLastLogin(user.lastLogin)}</span>
                  </div>
                </td>

                {/* Actions */}
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                    <button
                      onClick={() => onView(user)}
                      className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50
                               rounded-lg transition-all duration-200 transform hover:scale-105"
                      title="Просмотр"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => onEdit(user)}
                      className="p-2 text-green-600 hover:text-green-800 hover:bg-green-50
                               rounded-lg transition-all duration-200 transform hover:scale-105"
                      title="Редактировать"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => onChangePassword(user)}
                      className="p-2 text-orange-600 hover:text-orange-800 hover:bg-orange-50
                               rounded-lg transition-all duration-200 transform hover:scale-105"
                      title="Сменить пароль"
                    >
                      <Key className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => onDelete(user)}
                      className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50
                               rounded-lg transition-all duration-200 transform hover:scale-105"
                      title="Удалить"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};