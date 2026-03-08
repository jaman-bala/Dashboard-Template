// Backend API типы
export interface User {
  id: string;
  first_name: string | null;
  last_name: string | null;
  middle_name: string | null;
  email: string | null;
  phone: string;
  photo: string | null;
  roles: string[];
  is_active: boolean;
  last_login_iso: string | null;
  exit_login_iso: string | null;
}

export interface UserFormData {
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  email?: string;
  phone: string;
  roles?: string[];
  is_active?: boolean;
  password?: string;
  photo?: string | File;
}

// Вспомогательные типы для UI
export interface UserDisplay {
  id: string;
  firstName: string;
  lastName: string;
  middleName?: string;
  email?: string;
  phone: string;
  role: string;
  isActive: boolean;
  lastLogin?: Date;
  avatar?: string;
}

// Функция для преобразования User в UserDisplay
export const userToDisplay = (user: User): UserDisplay => ({
  id: user.id,
  firstName: user.first_name || '',
  lastName: user.last_name || '',
  middleName: user.middle_name || undefined,
  email: user.email || undefined,
  phone: user.phone,
  role: user.roles[0] || 'USER',
  isActive: user.is_active,
  lastLogin: user.last_login_iso ? new Date(user.last_login_iso) : undefined,
  avatar: user.photo || undefined,
});

// Функция для преобразования UserFormData в CreateUserRequest
export const formDataToCreateRequest = (formData: UserFormData) => ({
  first_name: formData.first_name,
  last_name: formData.last_name,
  middle_name: formData.middle_name,
  email: formData.email,
  phone: formData.phone,
  password: formData.password || '',
  roles: formData.roles || ['USER'],
  is_active: formData.is_active ?? true,
  photo: formData.photo,
});

// Функция для преобразования UserFormData в UpdateUserRequest
export const formDataToUpdateRequest = (formData: UserFormData) => ({
  first_name: formData.first_name,
  last_name: formData.last_name,
  middle_name: formData.middle_name,
  email: formData.email,
  phone: formData.phone,
  password: formData.password,
  roles: formData.roles,
  is_active: formData.is_active,
  // photo исключаем, так как он обновляется отдельно через updateUserAvatar
});
