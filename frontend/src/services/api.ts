import axios, { AxiosInstance, AxiosResponse } from 'axios';

// Типы для API
export interface LoginRequest {
  phone: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  access_token: string;
  last_login: string;
}

export interface UserResponse {
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

export interface CreateUserRequest {
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  email?: string;
  phone: string;
  password: string;
  photo?: string;
  roles?: string[];
  is_active?: boolean;
}

export interface UpdateUserRequest {
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  email?: string;
  phone?: string;
  password?: string;
  photo?: string;
  roles?: string[];
  is_active?: boolean;
}

export interface ChangePasswordRequest {
  new_password: string;
  change_password: string;
}

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: '/api/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Загружаем токен из localStorage при инициализации
    this.token = localStorage.getItem('access_token');
    if (this.token) {
      this.setAuthToken(this.token);
    }

    // Добавляем interceptor для автоматического добавления токена
    this.client.interceptors.request.use(
      (config: any) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error: any) => {
        return Promise.reject(error);
      }
    );

    // Добавляем interceptor для обработки ошибок авторизации
    this.client.interceptors.response.use(
      (response: any) => response,
      async (error: any) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            // Пытаемся обновить токен
            const refreshResponse = await this.refreshToken();
            this.setAuthToken(refreshResponse.access_token);

            // Повторяем оригинальный запрос с новым токеном
            originalRequest.headers.Authorization = `Bearer ${refreshResponse.access_token}`;
            return this.client(originalRequest);
          } catch (refreshError) {
            // Если refresh не удался, выходим
            this.logout();
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  setAuthToken(token: string) {
    this.token = token;
    localStorage.setItem('access_token', token);
    this.client.defaults.headers.Authorization = `Bearer ${token}`;
  }

  clearAuthToken() {
    this.token = null;
    localStorage.removeItem('access_token');
    delete this.client.defaults.headers.Authorization;
  }

  logout() {
    this.clearAuthToken();
    // Перенаправляем на страницу входа
    window.location.href = '/login';
  }

  // Аутентификация
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await this.client.post('/auth/login', credentials);
    const { access_token } = response.data;
    this.setAuthToken(access_token);
    return response.data;
  }

  async logoutUser(): Promise<void> {
    try {
      await this.client.delete('/auth/logout');
    } finally {
      this.logout();
    }
  }

  async getCurrentUser(): Promise<UserResponse> {
    const response: AxiosResponse<UserResponse> = await this.client.get('/auth/me');
    return response.data;
  }

  // Управление пользователями
  async getAllUsers(): Promise<UserResponse[]> {
    const response: AxiosResponse<UserResponse[]> = await this.client.get('/auth/get_all_users');
    return response.data;
  }

  async getUserById(userId: string): Promise<UserResponse> {
    const response: AxiosResponse<UserResponse> = await this.client.get(`/auth/get_users_by_id/${userId}`);
    return response.data;
  }

  async createUser(userData: CreateUserRequest): Promise<UserResponse> {
    const formData = new FormData();

    // Добавляем поля в FormData
    if (userData.first_name) formData.append('first_name', userData.first_name);
    if (userData.last_name) formData.append('last_name', userData.last_name);
    if (userData.middle_name) formData.append('middle_name', userData.middle_name);
    if (userData.email) formData.append('email', userData.email);
    formData.append('phone', userData.phone);
    formData.append('password', userData.password);
    if (userData.photo) formData.append('photo', userData.photo);
    if (userData.roles) {
      userData.roles.forEach(role => formData.append('roles', role));
    }
    formData.append('is_active', String(userData.is_active ?? true));

    const response: AxiosResponse<{ message: string; data: UserResponse }> = await this.client.post('/auth/create', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.data;
  }

  async updateUser(userId: string, userData: UpdateUserRequest): Promise<UserResponse> {
    const response: AxiosResponse<{ message: string; data: UserResponse }> = await this.client.patch(`/auth/update/${userId}`, userData);
    return response.data.data;
  }

  async updateUserAvatar(userId: string, photo: File): Promise<UserResponse> {
    const formData = new FormData();
    formData.append('photo', photo);

    const response: AxiosResponse<{ message: string; data: UserResponse }> = await this.client.patch(`/auth/update_avatar/${userId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data.data;
  }

  async deleteUser(userId: string): Promise<void> {
    await this.client.delete(`/auth/${userId}`);
  }

  async changePassword(userId: string, passwordData: ChangePasswordRequest): Promise<void> {
    await this.client.put(`/auth/change_password/${userId}`, passwordData);
  }

  async refreshToken(): Promise<{ access_token: string }> {
    const response = await this.client.post('/auth/refresh', {});
    return response.data;
  }

  // Проверка авторизации
  isAuthenticated(): boolean {
    return !!this.token;
  }

  getToken(): string | null {
    return this.token;
  }
}

// Создаем единственный экземпляр API клиента
export const apiClient = new ApiClient();
export default apiClient;
