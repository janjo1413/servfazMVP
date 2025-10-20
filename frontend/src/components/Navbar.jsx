import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navbar() {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-white shadow-lg mb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo/Título */}
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              ServFaz MVP
            </h1>
          </div>

          {/* Menu Items */}
          <div className="flex space-x-4">
            <Link
              to="/"
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/')
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              Gerar Cálculo
            </Link>

            <Link
              to="/historico"
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/historico')
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              Histórico de Cálculos
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
