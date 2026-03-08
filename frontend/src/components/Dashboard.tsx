import React, { useState, useMemo, useEffect } from 'react';
import { Plus, Users, UserCheck, UserX, Download, Upload, Menu, LogOut } from 'lucide-react';
import { User, UserFormData, UserDisplay, userToDisplay, formDataToCreateRequest, formDataToUpdateRequest } from '../types/User';
import { roleLabels } from '../utils/mockData';
import { SearchBar } from './SearchBar';
import { UserTable } from './UserTable';
import { UserModal } from './UserModal';
import { PasswordModal } from './PasswordModal';
import { ErrorModal } from './ErrorModal';
import { Sidebar } from './Sidebar';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/api';

export const Dashboard: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [displayUsers, setDisplayUsers] = useState<UserDisplay[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeMenuItem, setActiveMenuItem] = useState('users');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { user: currentUser, logout } = useAuth();

  // Загружаем пользователей при монтировании компонента
  useEffect(() => {
    loadUsers();
  }, []);

  // Обновляем displayUsers при изменении users
  useEffect(() => {
    const display = users.map(userToDisplay);
    setDisplayUsers(display);
  }, [users]);

  const loadUsers = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const usersData = await apiClient.getAllUsers();
      setUsers(usersData);
    } catch (err: any) {
      showError(err.response?.data?.detail || 'Ошибка загрузки пользователей', 'error', 'Ошибка загрузки');
    } finally {
      setIsLoading(false);
    }
  };

  // Modal states
  const [userModal, setUserModal] = useState<{
    isOpen: boolean;
    mode: 'add' | 'edit' | 'view';
    user?: User | null;
    fieldErrors?: {
      email?: string;
      phone?: string;
    };
  }>({
    isOpen: false,
    mode: 'add',
    user: null,
    fieldErrors: {}
  });

  const [passwordModal, setPasswordModal] = useState<{
    isOpen: boolean;
    user?: User | null;
  }>({
    isOpen: false,
    user: null
  });

  const [errorModal, setErrorModal] = useState<{
    isOpen: boolean;
    title?: string;
    message: string;
    type?: 'error' | 'warning' | 'info';
    fieldErrors?: { [key: string]: string };
  }>({
    isOpen: false,
    message: '',
    type: 'error',
    fieldErrors: {}
  });

  // Filtered users
  const filteredUsers = useMemo(() => {
    return displayUsers.filter(user => {
      const matchesSearch = searchTerm === '' ||
        user.firstName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.lastName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.middleName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.phone.includes(searchTerm);

      const matchesRole = selectedRole === 'all' || user.role === selectedRole;
      const matchesStatus = selectedStatus === 'all' ||
        (selectedStatus === 'active' && user.isActive) ||
        (selectedStatus === 'inactive' && !user.isActive);

      return matchesSearch && matchesRole && matchesStatus;
    });
  }, [displayUsers, searchTerm, selectedRole, selectedStatus]);

  // Statistics
  const stats = useMemo(() => {
    const total = displayUsers.length;
    const active = displayUsers.filter(u => u.isActive).length;
    const inactive = total - active;
    const admins = displayUsers.filter(u => u.role === 'ADMIN' || u.role === 'SUPERUSER').length;

    return { total, active, inactive, admins };
  }, [displayUsers]);

  // Handlers
  const handleAddUser = () => {
    setUserModal({ isOpen: true, mode: 'add', user: null });
  };

  const handleViewUser = (user: UserDisplay) => {
    const backendUser = users.find(u => u.id === user.id);
    setUserModal({ isOpen: true, mode: 'view', user: backendUser || null });
  };

  const handleEditUser = (user: UserDisplay) => {
    const backendUser = users.find(u => u.id === user.id);
    setUserModal({ isOpen: true, mode: 'edit', user: backendUser || null });
  };

  const handleDeleteUser = async (user: UserDisplay) => {
    if (window.confirm(`Вы уверены, что хотите удалить пользователя ${user.firstName} ${user.lastName}?`)) {
      try {
        await apiClient.deleteUser(user.id);
        await loadUsers(); // Перезагружаем список пользователей
      } catch (err: any) {
        showError(err.response?.data?.detail || 'Ошибка удаления пользователя', 'error', 'Ошибка удаления');
      }
    }
  };

  const handleChangePassword = (user: UserDisplay) => {
    const backendUser = users.find(u => u.id === user.id);
    setPasswordModal({ isOpen: true, user: backendUser || null });
  };

  const handleToggleUserStatus = async (user: UserDisplay) => {
    try {
      const backendUser = users.find(u => u.id === user.id);
      if (backendUser) {
        await apiClient.updateUser(user.id, { is_active: !user.isActive });
        await loadUsers(); // Перезагружаем список пользователей
      }
    } catch (err: any) {
      showError(err.response?.data?.detail || 'Ошибка изменения статуса пользователя', 'error', 'Ошибка изменения статуса');
    }
  };

  const handleSaveUser = async (userData: UserFormData) => {
    try {
      if (userModal.mode === 'add') {
        const createRequest = formDataToCreateRequest(userData);
        await apiClient.createUser(createRequest);
        await loadUsers(); // Перезагружаем список пользователей
      } else if (userModal.mode === 'edit' && userModal.user) {
        // Если есть новый файл аватара, используем специальный endpoint
        if (userData.photo instanceof File) {
          try {
            await apiClient.updateUserAvatar(userModal.user.id, userData.photo);
          } catch (avatarError: any) {
            showError(
              avatarError.response?.data?.detail || 'Ошибка обновления аватара',
              'error',
              'Ошибка обновления аватара'
            );
            return; // Прерываем выполнение, если аватар не обновился
          }
        }

        // Обновляем остальные данные пользователя
        const updateRequest = formDataToUpdateRequest(userData);
        await apiClient.updateUser(userModal.user.id, updateRequest);
        await loadUsers(); // Перезагружаем список пользователей
      }
      closeUserModal();
    } catch (err: any) {
      // Специальная обработка ошибок уникальности
      if (err.response?.status === 409) {
        const responseData = err.response.data;

        // Проверяем новую структуру ответа с полем
        if (responseData && typeof responseData === 'object' && responseData.field) {
          if (responseData.field === 'phone') {
            showError(
              'Пользователь с таким номером телефона уже существует. Пожалуйста, используйте другой номер телефона.',
              'error',
              'Ошибка уникальности',
              { phone: 'Этот номер телефона уже используется' }
            );
            // Также устанавливаем ошибку в поле формы
            setUserModal(prev => ({
              ...prev,
              fieldErrors: { phone: 'Этот номер телефона уже используется' }
            }));
          } else if (responseData.field === 'email') {
            showError(
              'Пользователь с таким email уже существует. Пожалуйста, используйте другой адрес электронной почты.',
              'error',
              'Ошибка уникальности',
              { email: 'Этот email уже используется' }
            );
            // Также устанавливаем ошибку в поле формы
            setUserModal(prev => ({
              ...prev,
              fieldErrors: { email: 'Этот email уже используется' }
            }));
          } else {
            showError(responseData.message || 'Произошла ошибка при сохранении пользователя', 'error', 'Ошибка сохранения');
          }
        }
        // Обратная совместимость со старым форматом
        else if (responseData && responseData.message && (responseData.message.includes('номером телефона') || responseData.message.includes('phone'))) {
          showError(
            'Пользователь с таким номером телефона уже существует. Пожалуйста, используйте другой номер телефона.',
            'error',
            'Ошибка уникальности',
            { phone: 'Этот номер телефона уже используется' }
          );
          // Также устанавливаем ошибку в поле формы
          setUserModal(prev => ({
            ...prev,
            fieldErrors: { phone: 'Этот номер телефона уже используется' }
          }));
        } else if (responseData && responseData.message && (responseData.message.includes('email') || responseData.message.includes('почтой'))) {
          showError(
            'Пользователь с таким email уже существует. Пожалуйста, используйте другой адрес электронной почты.',
            'error',
            'Ошибка уникальности',
            { email: 'Этот email уже используется' }
          );
          // Также устанавливаем ошибку в поле формы
          setUserModal(prev => ({
            ...prev,
            fieldErrors: { email: 'Этот email уже используется' }
          }));
        } else {
          showError(
            responseData.message || 'Произошла ошибка при сохранении пользователя',
            'error',
            'Ошибка сохранения'
          );
        }
      } else if (err.response?.data?.details && Array.isArray(err.response.data.details)) {
        // Если это массив ошибок валидации
        const errorMessages = err.response.data.details.map((error: any) => error.message).join(', ');

        // Устанавливаем ошибки в соответствующие поля
        const fieldErrors: { [key: string]: string } = {};
        err.response.data.details.forEach((error: any) => {
          fieldErrors[error.field] = error.message;
        });

        showError(
          `Ошибка валидации: ${errorMessages}`,
          'error',
          'Ошибка валидации данных',
          fieldErrors
        );

        // Также устанавливаем ошибки в поля формы
        const formFieldErrors: { email?: string; phone?: string } = {};
        err.response.data.details.forEach((error: any) => {
          if (error.field === 'email') {
            formFieldErrors.email = error.message;
          } else if (error.field === 'phone') {
            formFieldErrors.phone = error.message;
          }
        });

        setUserModal(prev => ({
          ...prev,
          fieldErrors: formFieldErrors
        }));
      } else if (err.response?.data?.detail) {
        // Проверяем, не является ли detail названием класса исключения
        const detail = err.response.data.detail;
        if (detail.includes('Exception') || detail.includes('Error')) {
          showError('Произошла ошибка при сохранении пользователя', 'error', 'Ошибка');
        } else {
          showError(detail, 'error', 'Ошибка');
        }
      } else {
        showError('Ошибка сохранения пользователя', 'error', 'Ошибка');
      }
    }
  };

  const handleSavePassword = async (passwords: { new: string; confirm: string }) => {
    if (!passwordModal.user) return;

    try {
      await apiClient.changePassword(passwordModal.user.id, {
        new_password: passwords.new,
        change_password: passwords.confirm
      });
      closePasswordModal();
    } catch (err: any) {
      showError(err.response?.data?.detail || 'Ошибка смены пароля', 'error', 'Ошибка смены пароля');
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  const closeUserModal = () => {
    setUserModal({ isOpen: false, mode: 'add', user: null, fieldErrors: {} });
  };

  const closePasswordModal = () => {
    setPasswordModal({ isOpen: false, user: null });
  };

  const showError = (message: string, type: 'error' | 'warning' | 'info' = 'error', title?: string, fieldErrors?: { [key: string]: string }) => {
    setErrorModal({
      isOpen: true,
      title,
      message,
      type,
      fieldErrors: fieldErrors || {}
    });
  };

  const closeErrorModal = () => {
    setErrorModal({
      isOpen: false,
      message: '',
      type: 'error',
      fieldErrors: {}
    });
  };

  const handleMenuItemClick = (item: string) => {
    setActiveMenuItem(item);
    // Here you can add navigation logic for different menu items
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/20 flex">
      {/* Sidebar */}
      <Sidebar
        isCollapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        activeItem={activeMenuItem}
        onItemClick={handleMenuItemClick}
      />

      {/* Main Content */}
      <div className={`
        flex-1 transition-all duration-300 ease-out
        ${sidebarCollapsed ? 'ml-20' : 'ml-72'}
      `}>
        {/* Mobile Header */}
        <div className="lg:hidden bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
          >
            <Menu className="w-6 h-6" />
          </button>
          <h1 className="text-lg font-semibold text-gray-900">Пользователи</h1>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 hidden lg:block">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Управление пользователями
              </h1>
              <p className="text-lg text-gray-600">
                Добро пожаловать в панель управления пользователями
              </p>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                {currentUser?.first_name} {currentUser?.last_name}
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Выйти
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">!</span>
              </div>
              <span>{typeof error === 'string' ? error : JSON.stringify(error)}</span>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-500 hover:text-red-700"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="text-center">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600">Загрузка пользователей...</p>
            </div>
          </div>
        )}

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6
                        transform transition-all duration-200 hover:shadow-lg hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Всего пользователей</p>
                <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600
                            rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6
                        transform transition-all duration-200 hover:shadow-lg hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Активных</p>
                <p className="text-3xl font-bold text-green-600">{stats.active}</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-green-600
                            rounded-xl flex items-center justify-center">
                <UserCheck className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6
                        transform transition-all duration-200 hover:shadow-lg hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Неактивных</p>
                <p className="text-3xl font-bold text-red-600">{stats.inactive}</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-br from-red-400 to-red-600
                            rounded-xl flex items-center justify-center">
                <UserX className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6
                        transform transition-all duration-200 hover:shadow-lg hover:scale-105">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Администраторов</p>
                <p className="text-3xl font-bold text-purple-600">{stats.admins}</p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-purple-600
                            rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Actions Bar */}
        <div className="flex flex-col lg:flex-row gap-4 mb-6">
          {/* Search */}
          <div className="flex-1">
            <SearchBar
              value={searchTerm}
              onChange={setSearchTerm}
              placeholder="Поиск по имени или номеру телефона..."
            />
          </div>

          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value)}
              className="px-4 py-3 border border-gray-200 rounded-xl bg-white/50 backdrop-blur-sm
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       transition-all duration-200"
            >
              <option value="all">Все роли</option>
              {Object.entries(roleLabels).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-4 py-3 border border-gray-200 rounded-xl bg-white/50 backdrop-blur-sm
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       transition-all duration-200"
            >
              <option value="all">Все статусы</option>
              <option value="active">Активные</option>
              <option value="inactive">Неактивные</option>
            </select>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleAddUser}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-500
                       hover:from-blue-600 hover:to-purple-600 text-white rounded-xl font-medium
                       transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
            >
              <Plus className="w-5 h-5" />
              Добавить
            </button>

            <button className="flex items-center gap-2 px-4 py-3 bg-white border border-gray-200
                             hover:bg-gray-50 text-gray-700 rounded-xl font-medium
                             transition-all duration-200 transform hover:scale-105">
              <Download className="w-5 h-5" />
              Экспорт
            </button>

            <button className="flex items-center gap-2 px-4 py-3 bg-white border border-gray-200
                             hover:bg-gray-50 text-gray-700 rounded-xl font-medium
                             transition-all duration-200 transform hover:scale-105">
              <Upload className="w-5 h-5" />
              Импорт
            </button>
          </div>
        </div>

        {/* Results Info */}
        {!isLoading && (
          <div className="mb-6">
            <p className="text-sm text-gray-600">
              Показано {filteredUsers.length} из {displayUsers.length} пользователей
            </p>
          </div>
        )}

        {/* Users Table */}
        {!isLoading && (
          <UserTable
            users={filteredUsers}
            onView={handleViewUser}
            onEdit={handleEditUser}
            onDelete={handleDeleteUser}
            onChangePassword={handleChangePassword}
            onToggleStatus={handleToggleUserStatus}
          />
        )}

        {/* User Modal */}
        <UserModal
          isOpen={userModal.isOpen}
          onClose={closeUserModal}
          onSave={handleSaveUser}
          user={userModal.user}
          mode={userModal.mode}
          fieldErrors={userModal.fieldErrors}
        />

        {/* Password Modal */}
        <PasswordModal
          isOpen={passwordModal.isOpen}
          onClose={closePasswordModal}
          onSave={handleSavePassword}
          userName={passwordModal.user ?
            `${passwordModal.user.first_name || ''} ${passwordModal.user.last_name || ''}` : ''}
        />

        {/* Error Modal */}
        <ErrorModal
          isOpen={errorModal.isOpen}
          onClose={closeErrorModal}
          title={errorModal.title}
          message={errorModal.message}
          type={errorModal.type}
          fieldErrors={errorModal.fieldErrors}
        />
        </div>
      </div>
    </div>
  );
};
