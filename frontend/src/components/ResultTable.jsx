import React from 'react';

function ResultTable({ results }) {
  if (!results || !results.results_base) {
    return null;
  }

  const formatValue = (value) => {
    if (value === null || value === undefined || value === '') {
      return '-';
    }
    
    // Se for número, formatar com separador de milhares
    if (typeof value === 'number') {
      return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(value);
    }
    
    return value;
  };

  const isAccordoBlock = (titulo) => {
    return titulo && titulo.toUpperCase().includes('TOTAL DO VALOR PROPOSTO PARA ACORDO');
  };

  const renderTables = (tablesList, sectionTitle, bgColor = 'bg-blue-50', borderColor = 'border-blue-500', textColor = 'text-blue-700') => {
    if (!tablesList || tablesList.length === 0) return null;

    return (
      <div className="mb-12">
        {/* Título da Seção */}
        <div className={`${bgColor} border-l-4 ${borderColor} p-4 mb-6`}>
          <h2 className={`text-2xl font-bold ${textColor}`}>
            {sectionTitle}
          </h2>
        </div>

        {/* Tabelas */}
        <div className="space-y-8">
          {tablesList.map((block, blockIndex) => {
            const isAcordo = isAccordoBlock(block.titulo);
            
            return (
              <div 
                key={blockIndex} 
                className={`bg-white rounded-lg shadow-md overflow-hidden ${
                  isAcordo ? 'border-4 border-emerald-600' : ''
                }`}
              >
                {/* Título do Bloco */}
                <div className={`px-6 py-4 ${
                  isAcordo ? 'bg-emerald-100' : 'bg-gray-100'
                } border-b border-gray-200`}>
                  <h3 className={`text-lg font-semibold ${
                    isAcordo ? 'text-emerald-800' : 'text-gray-800'
                  }`}>
                    {block.titulo}
                  </h3>
                  {isAcordo && (
                    <p className="text-sm text-emerald-700 mt-1 font-medium">
                      ⭐ Valor Final Proposto para Acordo
                    </p>
                  )}
                </div>

                {/* Tabela */}
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    {/* Cabeçalho */}
                    <thead className="bg-gray-50">
                      <tr>
                        {block.header.map((headerCell, headerIndex) => (
                          <th
                            key={headerIndex}
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          >
                            {headerCell}
                          </th>
                        ))}
                      </tr>
                    </thead>

                    {/* Corpo */}
                    <tbody className="bg-white divide-y divide-gray-200">
                      {block.rows && block.rows.length > 0 ? (
                        block.rows.map((row, rowIndex) => (
                          <tr key={rowIndex} className="hover:bg-gray-50">
                            {row.map((cell, cellIndex) => (
                              <td
                                key={cellIndex}
                                className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                              >
                                {formatValue(cell)}
                              </td>
                            ))}
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td
                            colSpan={block.header.length}
                            className="px-6 py-4 text-center text-sm text-gray-500"
                          >
                            Sem dados
                          </td>
                        </tr>
                      )}

                      {/* Linha de Total */}
                      {block.total && (
                        <tr className={`${
                          isAcordo ? 'bg-emerald-50' : 'bg-gray-50'
                        } font-semibold`}>
                          {block.total.map((cell, cellIndex) => (
                            <td
                              key={cellIndex}
                              className={`px-6 py-4 whitespace-nowrap text-sm ${
                                isAcordo ? 'text-emerald-900' : 'text-gray-900'
                              }`}
                            >
                              {formatValue(cell)}
                            </td>
                          ))}
                          {/* Preencher células vazias se total tiver menos colunas que header */}
                          {Array.from({ 
                            length: block.header.length - block.total.length 
                          }).map((_, emptyIndex) => (
                            <td
                              key={`empty-${emptyIndex}`}
                              className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                            >
                              -
                            </td>
                          ))}
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Info Header */}
      <div className="bg-slate-50 border-l-4 border-slate-600 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-slate-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-slate-700">
              <strong>ID do Cálculo:</strong> {results.id}
            </p>
            <p className="text-sm text-slate-700 mt-1">
              <strong>Data:</strong> {new Date(results.created_at).toLocaleString('pt-BR')}
            </p>
            {results.correcao_ate && (
              <p className="text-sm text-slate-700 mt-1">
                <strong>Correção até:</strong> {results.correcao_ate}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Resultados Base (sempre mostrados) */}
      {renderTables(
        results.results_base,
        'Resultados Base (01/01/2025)',
        'bg-slate-50',
        'border-slate-600',
        'text-slate-800'
      )}

      {/* Resultados Atualizados com SELIC (apenas se existirem) */}
      {results.results_atualizados && results.results_atualizados.length > 0 && (
        <>
          <div className="border-t-4 border-amber-400 my-12"></div>
          {renderTables(
            results.results_atualizados,
            `Resultados Atualizados com SELIC (até ${results.correcao_ate})`,
            'bg-amber-50',
            'border-amber-600',
            'text-amber-900'
          )}
        </>
      )}

      {/* Botão para Nova Consulta */}
      <div className="pt-4">
        <button
          onClick={() => window.location.reload()}
          className="w-full bg-slate-700 text-white py-3 px-6 rounded-md hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-600 focus:ring-offset-2 transition-colors font-medium"
        >
          Nova Consulta
        </button>
      </div>
    </div>
  );
}

export default ResultTable;
