import React, { useState, useEffect } from 'react';
import { getApiUrl, getDefaultHeaders } from '../config/api';

function SelicPanel() {
  const [selicData, setSelicData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchSelicStatus();
  }, []);

  const fetchSelicStatus = async () => {
    try {
      const response = await fetch(getApiUrl('/selic/status'), {
        headers: getDefaultHeaders(),
      });
      if (!response.ok) {
        throw new Error('Erro ao buscar dados SELIC');
      }
      const data = await response.json();
      
      // Converter os meses da API para o formato do componente
      // Filtrar apenas meses >= 2025-01 (a partir de Janeiro/2025)
      const mesesFormatados = data.ultimos_12_meses
        ?.filter(item => item.mes >= '2025-01')
        ?.map(item => ({
          mes: item.mes,
          nome: formatarMesNome(
            parseInt(item.mes.split('-')[1]),
            parseInt(item.mes.split('-')[0])
          ),
          taxa: item.taxa
        })) || [];
      
      setSelicData({
        ...data,
        meses_recentes: mesesFormatados
      });
      
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const formatarMesNome = (mes, ano) => {
    const meses = [
      'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
      'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
    ];
    return `${meses[mes - 1]}/${ano}`;
  };

  const formatarProximaAtualizacao = (isoDate) => {
    if (!isoDate) return 'N/A';
    const date = new Date(isoDate);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <>
      {/* Botão para abrir painel */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed right-0 top-1/2 -translate-y-1/2 bg-amber-600 text-white px-3 py-6 rounded-l-lg shadow-lg hover:bg-amber-700 transition-all z-40"
        title="Ver taxas SELIC disponíveis"
      >
        <div className="flex flex-col items-center gap-1">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span className="text-xs font-medium writing-mode-vertical">SELIC</span>
        </div>
      </button>

      {/* Overlay transparente */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-20 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Painel lateral */}
      <div
        className={`fixed right-0 top-0 h-full w-80 bg-white shadow-2xl z-50 transform transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="bg-slate-800 text-white p-4 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold">Taxas SELIC</h3>
              <p className="text-xs text-slate-300">Últimos meses disponíveis</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-amber-400 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Conteúdo */}
          <div className="flex-1 overflow-y-auto p-4">
            {loading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-600"></div>
              </div>
            ) : error ? (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            ) : (
              <>
                {/* Informações do Cache */}
                {selicData.cache && (
                  <div className="bg-slate-50 rounded-lg p-4 mb-4">
                    <h4 className="text-sm font-semibold text-slate-700 mb-3">Status do Cache</h4>
                    <div className="space-y-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-slate-600">Total de meses:</span>
                        <span className="font-medium text-slate-900">{selicData.cache.total_meses}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Último mês:</span>
                        <span className="font-medium text-amber-600">
                          {formatarMesNome(
                            parseInt(selicData.cache.ultimo_mes?.split('-')[1]),
                            parseInt(selicData.cache.ultimo_mes?.split('-')[0])
                          )}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600">Taxa atual:</span>
                        <span className="font-medium text-emerald-600">
                          {selicData.cache.taxa_ultimo_mes?.toFixed(2)}%
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Scheduler Info */}
                {selicData.scheduler && (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <div className={`w-2 h-2 rounded-full ${selicData.scheduler.ativo ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
                      <h4 className="text-sm font-semibold text-slate-700">
                        {selicData.scheduler.ativo ? 'Atualização Automática Ativa' : 'Atualização Inativa'}
                      </h4>
                    </div>
                    <div className="space-y-1 text-xs text-slate-600">
                      <p>Horário: <span className="font-medium text-slate-900">{selicData.scheduler.horario_agendado}</span></p>
                      <p>Próxima: <span className="font-medium text-amber-700">
                        {formatarProximaAtualizacao(selicData.scheduler.proxima_atualizacao)}
                      </span></p>
                    </div>
                  </div>
                )}

                {/* Lista de Meses Recentes */}
                <div>
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Meses Disponíveis (a partir de Jan/2025)</h4>
                  <div className="space-y-2">
                    {selicData.meses_recentes?.map((item, index) => (
                      <div
                        key={item.mes}
                        className={`flex items-center justify-between p-3 rounded-lg border ${
                          index === selicData.meses_recentes.length - 1
                            ? 'bg-amber-50 border-amber-300'
                            : 'bg-white border-slate-200'
                        }`}
                      >
                        <div className="flex flex-col">
                          <span className={`text-sm font-medium ${
                            index === selicData.meses_recentes.length - 1
                              ? 'text-amber-900'
                              : 'text-slate-700'
                          }`}>
                            {item.nome}
                          </span>
                          {index === selicData.meses_recentes.length - 1 && (
                            <span className="text-xs text-amber-600 font-medium">Mais recente</span>
                          )}
                        </div>
                        <span className={`text-sm font-semibold ${
                          index === selicData.meses_recentes.length - 1
                            ? 'text-amber-700'
                            : 'text-emerald-600'
                        }`}>
                          {item.taxa?.toFixed(2)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Nota sobre N-1 */}
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-xs text-blue-800">
                    <span className="font-semibold">Nota:</span> O sistema usa apenas meses completos (mês atual - 1) 
                    para garantir a precisão dos dados.
                  </p>
                </div>
              </>
            )}
          </div>

          {/* Footer com botão de atualizar */}
          <div className="border-t border-slate-200 p-4">
            <button
              onClick={fetchSelicStatus}
              className="w-full bg-amber-600 text-white py-2 rounded-lg hover:bg-amber-700 transition-colors text-sm font-medium flex items-center justify-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Atualizar
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default SelicPanel;
