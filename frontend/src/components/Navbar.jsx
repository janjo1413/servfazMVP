import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navbar() {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-slate-800 shadow-lg mb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo/Título */}
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-white">
              ServFaz MVP
            </h1>
          </div>

          {/* Menu Items */}
          <div className="flex space-x-4">
            <Link
              to="/"
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/')
                  ? 'bg-amber-600 text-white'
                  : 'text-slate-200 hover:bg-slate-700 hover:text-white'
              }`}
            >
              Gerar Cálculo
            </Link>

            <Link
              to="/historico"
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/historico')
                  ? 'bg-amber-600 text-white'
                  : 'text-slate-200 hover:bg-slate-700 hover:text-white'
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
