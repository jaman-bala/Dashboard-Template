import { User } from '../types/User';

export const mockUsers: User[] = [
  {
    id: '1',
    avatar: 'https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg?auto=compress&cs=tinysrgb&w=150',
    firstName: 'Александр',
    lastName: 'Иванов',
    middleName: 'Петрович',
    email: 'a.ivanov@company.ru',
    phone: '+7 (999) 123-45-67',
    role: 'admin',
    isActive: true,
    createdAt: new Date('2024-01-15'),
    lastLogin: new Date('2024-12-20T10:30:00')
  },
  {
    id: '2',
    avatar: 'https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg?auto=compress&cs=tinysrgb&w=150',
    firstName: 'Мария',
    lastName: 'Петрова',
    middleName: 'Сергеевна',
    email: 'm.petrova@company.ru',
    phone: '+7 (999) 234-56-78',
    role: 'manager',
    isActive: true,
    createdAt: new Date('2024-02-10'),
    lastLogin: new Date('2024-12-19T16:45:00')
  },
  {
    id: '3',
    avatar: 'https://images.pexels.com/photos/91227/pexels-photo-91227.jpeg?auto=compress&cs=tinysrgb&w=150',
    firstName: 'Дмитрий',
    lastName: 'Смирнов',
    middleName: 'Александрович',
    phone: '+7 (999) 345-67-89',
    role: 'user',
    isActive: false,
    createdAt: new Date('2024-03-05'),
    lastLogin: new Date('2024-12-10T09:15:00')
  },
  {
    id: '4',
    avatar: 'https://images.pexels.com/photos/1681010/pexels-photo-1681010.jpeg?auto=compress&cs=tinysrgb&w=150',
    firstName: 'Елена',
    lastName: 'Козлова',
    middleName: 'Викторовна',
    email: 'e.kozlova@company.ru',
    phone: '+7 (999) 456-78-90',
    role: 'user',
    isActive: true,
    createdAt: new Date('2024-04-12'),
    lastLogin: new Date('2024-12-18T14:20:00')
  },
  {
    id: '5',
    avatar: 'https://images.pexels.com/photos/697509/pexels-photo-697509.jpeg?auto=compress&cs=tinysrgb&w=150',
    firstName: 'Андрей',
    lastName: 'Волков',
    middleName: 'Михайлович',
    email: 'a.volkov@company.ru',
    phone: '+7 (999) 567-89-01',
    role: 'manager',
    isActive: true,
    createdAt: new Date('2024-05-08'),
    lastLogin: new Date('2024-12-17T11:30:00')
  }
];

export const roleLabels = {
  ADMIN: 'Администратор',
  MANAGER: 'Менеджер',
  USER: 'Пользователь',
  SUPERUSER: 'Суперпользователь',
  CLIENT: 'Клиент'
};

export const roleColors = {
  ADMIN: 'bg-red-100 text-red-800 border-red-200',
  MANAGER: 'bg-blue-100 text-blue-800 border-blue-200',
  USER: 'bg-green-100 text-green-800 border-green-200',
  SUPERUSER: 'bg-purple-100 text-purple-800 border-purple-200',
  CLIENT: 'bg-gray-100 text-gray-800 border-gray-200'
};
