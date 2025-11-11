import React, { useState, useEffect } from 'react';
import ResultTable from '../components/ResultTable';
import { getApiUrl, getDefaultHeaders } from '../config/api';

function Historico() {
  const [calculos, setCalculos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCalculo, setSelectedCalculo] = useState(null);
  const [viewMode, setViewMode] = useState('list'); // 'list' ou 'details'
  const [bulkLoading, setBulkLoading] = useState(false);

  // Carregar lista de cálculos ao montar o componente
  useEffect(() => {
    fetchCalculos();
  }, []);

  const fetchCalculos = async () => {
    setLoading(true);
    setError(null);

    try {
      const url = getApiUrl('/results');
      console.log('🔍 [HISTORICO] Tentando buscar de:', url);
      
      const response = await fetch(url, {
        headers: getDefaultHeaders(),
      });
      
      console.log('📡 [HISTORICO] Status:', response.status);
      console.log('📡 [HISTORICO] Headers:', response.headers.get('content-type'));
      
      if (!response.ok) {
        const text = await response.text();
        console.error('❌ [HISTORICO] Erro - Response text:', text.substring(0, 200));
        throw new Error('Erro ao carregar histórico');
      }

      const data = await response.json();
      console.log('✅ [HISTORICO] Dados recebidos:', data);
      setCalculos(data.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerDetalhes = async (calculoId) => {
    try {
      const response = await fetch(getApiUrl(`/results/${calculoId}`), {
        headers: getDefaultHeaders(),
      });
      
      if (!response.ok) {
        throw new Error('Erro ao carregar detalhes');
      }

      const data = await response.json();
      
      // Transformar dados para o formato esperado pelo ResultTable
      const transformedData = {
        id: data.id,
        created_at: data.created_at,
        correcao_ate: data.output_data?.correcao_ate || data.input_data?.['correção_até'],
        results_base: data.output_data?.results_base || [],
        results_atualizados: data.output_data?.results_atualizados || null,
      };
      
      setSelectedCalculo(transformedData);
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
      const response = await fetch(getApiUrl(`/results/${calculoId}`), {
        method: 'DELETE',
        headers: getDefaultHeaders(),
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

  const handleAtualizarSelic = async (calculoId) => {
    // Confirmar com o usuário
    if (!confirm('Deseja atualizar este cálculo para a última data SELIC disponível?')) {
      return;
    }

    // Encontrar o botão e mostrar loading
    const botaoElement = event.target.closest('button');
    const textoOriginal = botaoElement.innerHTML;
    botaoElement.disabled = true;
    botaoElement.innerHTML = `
      <svg class="animate-spin h-4 w-4 mr-1.5 inline" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      Atualizando...
    `;

    try {
      const response = await fetch(getApiUrl(`/results/${calculoId}/atualizar`), {
        method: 'POST',
        headers: getDefaultHeaders(),
      });

      const data = await response.json();

      if (!response.ok) {
        // Erro específico: já está atualizado
        if (response.status === 400) {
          // Extrair mês/ano da mensagem de erro
          const match = data.detail.match(/\(([^)]+)\)/);
          const mesAno = match ? match[1] : 'o mês mais recente';
          
          // Mostrar modal customizado
          mostrarModalJaAtualizado(mesAno);
          return;
        }
        
        throw new Error(data.detail || 'Erro ao atualizar cálculo');
      }

      // Sucesso: redirecionar para ver detalhes
      alert(`Cálculo atualizado com sucesso!\nDe: ${data.data_anterior}\nPara: ${data.data_nova}`);
      handleVerDetalhes(calculoId);
      
    } catch (err) {
      alert(`Erro: ${err.message}`);
    } finally {
      // Restaurar botão
      if (botaoElement) {
        botaoElement.disabled = false;
        botaoElement.innerHTML = textoOriginal;
      }
    }
  };

  const mostrarModalJaAtualizado = (mesAno) => {
    // Criar modal customizado
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50';
    modal.innerHTML = `
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3 text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-amber-100">
            <svg class="h-6 w-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <h3 class="text-lg leading-6 font-medium text-gray-900 mt-4">Cálculo já atualizado</h3>
          <div class="mt-2 px-7 py-3">
            <p class="text-sm text-gray-500">
              Este cálculo já está atualizado para o mês mais recente disponível:
            </p>
            <p class="text-base font-semibold text-gray-900 mt-2">
              ${mesAno}
            </p>
          </div>
          <div class="items-center px-4 py-3">
            <button
              id="modal-ok-btn"
              class="px-4 py-2 bg-amber-600 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-amber-500"
            >
              OK
            </button>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Adicionar event listener para fechar
    const botaoOk = modal.querySelector('#modal-ok-btn');
    const fecharModal = () => {
      document.body.removeChild(modal);
    };
    
    botaoOk.addEventListener('click', fecharModal);
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        fecharModal();
      }
    });
  };

  const handleVoltar = () => {
    setSelectedCalculo(null);
    setViewMode('list');
    fetchCalculos(); // Recarregar lista ao voltar
  };

  const handleAtualizarTodos = async () => {
    if (!confirm('Deseja atualizar TODOS os cálculos para a última SELIC disponível?\n\nEsta operação pode demorar alguns minutos.')) {
      return;
    }

    setBulkLoading(true);

    try {
      const response = await fetch(getApiUrl('/results/atualizar-todos'), {
        method: 'POST',
        headers: getDefaultHeaders(),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erro ao atualizar cálculos');
      }

      // Mostrar relatório
      const { total, sucessos, erros, ja_atualizados, data_selic } = data;
      
      let mensagem = `Atualização Concluída!\n\n`;
      mensagem += `Total de cálculos: ${total}\n`;
      mensagem += `Data SELIC: ${data_selic}\n\n`;
      mensagem += `Atualizados: ${sucessos.length}\n`;
      mensagem += `Já estavam atualizados: ${ja_atualizados.length}\n`;
      
      if (erros.length > 0) {
        mensagem += `\nErros: ${erros.length}\n`;
        erros.forEach(erro => {
          mensagem += `  - ${erro.municipio}: ${erro.erro}\n`;
        });
      }

      alert(mensagem);
      fetchCalculos(); // Recarregar lista
    } catch (err) {
      alert(`Erro: ${err.message}`);
    } finally {
      setBulkLoading(false);
    }
  };

  const handleDeletarTodos = async () => {
    if (!confirm('ATENÇÃO: Deseja DELETAR TODOS os cálculos?\n\nEsta ação é IRREVERSÍVEL!')) {
      return;
    }

    if (!confirm('Confirma novamente? Esta operação não pode ser desfeita!')) {
      return;
    }

    try {
      const response = await fetch(getApiUrl('/results'), {
        method: 'DELETE',
        headers: getDefaultHeaders(),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Erro ao deletar cálculos');
      }

      alert(`${data.total_deletados} cálculos foram deletados com sucesso!`);
      fetchCalculos(); // Recarregar lista
    } catch (err) {
      alert(`Erro: ${err.message}`);
    }
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
            {selectedCalculo.updated_at && (
              <div className="md:col-span-2">
                <p className="text-sm text-gray-600">Última Atualização</p>
                <p className="font-medium text-amber-700">{formatDate(selectedCalculo.updated_at)}</p>
              </div>
            )}
            {selectedCalculo.input_data && (
              <>
                <div>
                  <p className="text-sm text-gray-600">Município</p>
                  <p className="font-medium">{selectedCalculo.input_data.município}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Correção até</p>
                  <p className="font-medium">
                    {selectedCalculo.output_data?.correcao_ate || selectedCalculo.input_data.correção_até}
                    {selectedCalculo.output_data?.correcao_anterior && (
                      <span className="text-sm text-gray-500 ml-2">
                        (Antes era {selectedCalculo.output_data.correcao_anterior})
                      </span>
                    )}
                  </p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Resultados */}
        <ResultTable results={selectedCalculo} />
      </div>
    );
  }

  // Modo: Listagem
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="text-center mb-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Histórico de Cálculos
        </h2>
        <p className="text-lg text-gray-600">
          Visualize e gerencie todos os cálculos realizados
        </p>
      </div>

      {/* Botões de Ações em Lote */}
      {!loading && calculos.length > 0 && (
        <div className="flex justify-center gap-4 mb-6">
          <button
            onClick={handleAtualizarTodos}
            disabled={bulkLoading}
            className="inline-flex items-center px-6 py-3 border border-amber-400 rounded-lg text-amber-800 bg-amber-50 hover:bg-amber-100 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {bulkLoading ? (
              <>
                <svg className="animate-spin h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Atualizando todos...
              </>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Atualizar Todos
              </>
            )}
          </button>

          <button
            onClick={handleDeletarTodos}
            disabled={bulkLoading}
            className="inline-flex items-center px-6 py-3 border border-red-400 rounded-lg text-red-800 bg-red-50 hover:bg-red-100 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Deletar Todos (Temp)
          </button>
        </div>
      )}

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
                    Criado em
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Atualizado em
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Município
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Correção até
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {calculo.updated_at ? (
                        <span className="text-amber-700 font-medium">
                          {formatDate(calculo.updated_at)}
                        </span>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {calculo.município}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex flex-col">
                        <span className="text-gray-900 font-medium">
                          {calculo.correcao_ate || calculo.correção_até}
                        </span>
                        {calculo.correcao_anterior && (
                          <span className="text-xs text-gray-500">
                            Antes era {calculo.correcao_anterior}
                          </span>
                        )}
                      </div>
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
