import React from 'react';

function Historico() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Histórico de Cálculos
        </h2>
        <p className="text-lg text-gray-600">
          Visualize e gerencie todos os cálculos realizados
        </p>
      </div>

      {/* Placeholder - Empty State */}
      <div className="bg-white rounded-lg shadow-md p-12">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-xl font-medium text-gray-900">
            Em Desenvolvimento
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            Esta página exibirá o histórico completo de cálculos realizados.
          </p>
          <div className="mt-6">
            <div className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white">
              Funcionalidade em construção
            </div>
          </div>
        </div>
      </div>

      {/* Preview do que virá */}
      <div className="mt-8 bg-blue-50 border-l-4 border-blue-500 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">
              Próximas funcionalidades:
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <ul className="list-disc list-inside space-y-1">
                <li>Listagem de todos os cálculos realizados</li>
                <li>Filtro por data, município e status</li>
                <li>Visualização detalhada de cada cálculo</li>
                <li>Exportação de resultados em PDF</li>
                <li>Comparação entre diferentes cálculos</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Historico;
