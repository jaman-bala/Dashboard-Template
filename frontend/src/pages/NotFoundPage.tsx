import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft, Search } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        {/* Анимированная иконка 404 */}
        <div className="mb-8">
          <div className="relative">
            <div className="text-9xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 animate-pulse">
              404
            </div>
            <div className="absolute -top-4 -right-4 w-8 h-8 bg-red-500 rounded-full animate-bounce"></div>
          </div>
        </div>

        {/* Заголовок */}
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          Страница не найдена
        </h1>

        {/* Описание */}
        <p className="text-xl text-gray-600 mb-8 leading-relaxed">
          К сожалению, запрашиваемая страница не существует или была перемещена.
          Возможно, вы ввели неправильный адрес или перешли по устаревшей ссылке.
        </p>

        {/* Кнопки действий */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
          <Link
            to="/dashboard"
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600
                     text-white font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700
                     transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
          >
            <Home className="w-5 h-5 mr-2" />
            На главную
          </Link>

          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center px-6 py-3 bg-white text-gray-700 font-semibold
                     rounded-xl border-2 border-gray-200 hover:border-gray-300
                     transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Назад
          </button>
        </div>

        {/* Поиск */}
        <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Ищете что-то конкретное?
          </h3>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Введите запрос..."
              className="flex-1 px-4 py-3 border border-gray-200 rounded-xl
                       focus:ring-2 focus:ring-blue-500 focus:border-transparent
                       transition-all duration-200"
            />
            <button className="px-6 py-3 bg-blue-600 text-white rounded-xl
                              hover:bg-blue-700 transition-all duration-200
                              transform hover:scale-105">
              <Search className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Дополнительная информация */}
        <div className="mt-8 text-sm text-gray-500">
          <p>
            Если проблема повторяется, обратитесь к администратору системы
          </p>
        </div>
      </div>
    </div>
  );
};
