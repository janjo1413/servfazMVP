import React, { useState, useEffect } from 'react';
import ResultTable from '../components/ResultTable';

function Historico() {
  const [calculos, setCalculos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCalculo, setSelectedCalculo] = useState(null);
  const [viewMode, setViewMode] = useState('list'); // 'list' ou 'details'

  // Carregar lista de cálculos ao montar o componente
  useEffect(() => {
    fetchCalculos();
  }, []);

  const fetchCalculos = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/results');
      
      if (!response.ok) {
        throw new Error('Erro ao carregar histórico');
      }

      const data = await response.json();
      setCalculos(data.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerDetalhes = async (calculoId) => {
    try {
      const response = await fetch(`/api/results/${calculoId}`);
      
      if (!response.ok) {
        throw new Error('Erro ao carregar detalhes');
      }

      const data = await response.json();
      setSelectedCalculo(data);
      setViewMode('details');
    } catch (err) {
      alert(`Erro: ${err.message}`);
    }
  };

  const handleDeletar = async (calculoId) => {
    if (!confirm('Tem certeza que deseja deletar este cálculo?')) {
      return;
    }

    try {
      const response = await fetch(`/api/results/${calculoId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Erro ao deletar cálculo');
      }

      // Atualizar lista
      fetchCalculos();
      alert('Cálculo deletado com sucesso!');
    } catch (err) {
      alert(`Erro: ${err.message}`);
    }
  };

  const handleAtualizarSelic = (calculoId) => {
    // Placeholder - funcionalidade futura
    alert('Funcionalidade "Atualizar para SELIC Atual" será implementada em breve!');
  };

  const handleVoltar = () => {
    setSelectedCalculo(null);
    setViewMode('list');
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZone: 'America/Sao_Paulo'
      });
    } catch {
      return dateString;
    }
  };

  // Modo: Visualização de Detalhes
  if (viewMode === 'details' && selectedCalculo) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header com botão voltar */}
        <div className="mb-6">
          <button
            onClick={handleVoltar}
            className="flex items-center text-slate-700 hover:text-slate-900 font-medium"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Voltar para Lista
          </button>
        </div>

        {/* Informações do Cálculo */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Detalhes do Cálculo</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">ID do Cálculo</p>
              <p className="font-mono text-sm">{selectedCalculo.id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Data de Criação</p>
              <p className="font-medium">{formatDate(selectedCalculo.created_at)}</p>
            </div>
            {selectedCalculo.input_data && (
              <>
                <div>
                  <p className="text-sm text-gray-600">Município</p>
                  <p className="font-medium">{selectedCalculo.input_data.município}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Correção até</p>
                  <p className="font-medium">{selectedCalculo.input_data.correção_até}</p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Resultados */}
        {selectedCalculo.output_data && (
          <ResultTable 
            results={{
              id: selectedCalculo.id,
              created_at: selectedCalculo.created_at,
              correcao_ate: selectedCalculo.input_data?.correção_até,
              results_base: selectedCalculo.output_data.results_base,
              results_atualizados: selectedCalculo.output_data.results_atualizados
            }} 
          />
        )}
      </div>
    );
  }

  // Modo: Listagem
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

      {/* Loading */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Lista de Cálculos */}
      {!loading && !error && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {calculos.length === 0 ? (
            // Empty State
            <div className="p-12 text-center">
              <svg
                className="mx-auto h-16 w-16 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="mt-4 text-xl font-medium text-gray-900">
                Nenhum cálculo encontrado
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Comece gerando um novo cálculo na página inicial.
              </p>
            </div>
          ) : (
            // Tabela de Cálculos
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Data
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Município
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Correção até
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {calculos.map((calculo) => (
                  <tr key={calculo.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(calculo.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {calculo.município}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {calculo.correção_até}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                      {calculo.id.substring(0, 8)}...
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end gap-3">
                        <button
                          onClick={() => handleVerDetalhes(calculo.id)}
                          className="inline-flex items-center px-3 py-1.5 border border-slate-300 rounded-md text-slate-700 bg-slate-50 hover:bg-slate-100 transition-colors"
                          title="Ver Detalhes"
                        >
                          <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                          Ver Detalhes
                        </button>
                        <button
                          onClick={() => handleAtualizarSelic(calculo.id)}
                          className="inline-flex items-center px-3 py-1.5 border border-amber-300 rounded-md text-amber-800 bg-amber-50 hover:bg-amber-100 transition-colors"
                          title="Atualizar para SELIC Atual"
                        >
                          <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                          Atualizar
                        </button>
                        <button
                          onClick={() => handleDeletar(calculo.id)}
                          className="inline-flex items-center px-3 py-1.5 border border-red-300 rounded-md text-red-800 bg-red-50 hover:bg-red-100 transition-colors"
                          title="Deletar Cálculo"
                        >
                          <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                          Deletar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Info Footer */}
      {!loading && !error && calculos.length > 0 && (
        <div className="mt-4 text-center text-sm text-gray-500">
          Total de cálculos: {calculos.length}
        </div>
      )}
    </div>
  );
}

export default Historico;
