import React, { useState } from 'react';
import ResultTable from './components/ResultTable';

function App() {
  const [formData, setFormData] = useState({
    município: '',
    ajuizamento: '',
    citação: '',
    início_cálculo: '',
    final_cálculo: '',
    honorários_s_valor_da_condenação: '',
    honorários_em_valor_fixo: 0,
    deságio_a_aplicar_sobre_o_principal: 0,
    deságio_em_a_aplicar_em_honorários: 0,
    correção_até: '',
  });

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'number' ? parseFloat(value) || 0 : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('/api/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erro ao processar cálculo');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            ServFaz MVP
          </h1>
          <p className="text-lg text-gray-600">
            Sistema de Cálculo Jurídico
          </p>
        </div>

        {/* Formulário */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">
            Dados do Processo
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Município */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Município
                </label>
                <input
                  type="text"
                  name="município"
                  value={formData.município}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Ajuizamento */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data de Ajuizamento
                </label>
                <input
                  type="text"
                  name="ajuizamento"
                  value={formData.ajuizamento}
                  onChange={handleChange}
                  required
                  placeholder="DD/MM/AAAA"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Citação */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data de Citação
                </label>
                <input
                  type="text"
                  name="citação"
                  value={formData.citação}
                  onChange={handleChange}
                  required
                  placeholder="DD/MM/AAAA"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Início Cálculo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Início do Cálculo
                </label>
                <input
                  type="text"
                  name="início_cálculo"
                  value={formData.início_cálculo}
                  onChange={handleChange}
                  required
                  placeholder="DD/MM/AAAA"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Final Cálculo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Final do Cálculo
                </label>
                <input
                  type="text"
                  name="final_cálculo"
                  value={formData.final_cálculo}
                  onChange={handleChange}
                  required
                  placeholder="DD/MM/AAAA"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Correção Até */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Correção Até
                </label>
                <input
                  type="text"
                  name="correção_até"
                  value={formData.correção_até}
                  onChange={handleChange}
                  required
                  placeholder="DD/MM/AAAA"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Honorários Percentual */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Honorários s/ Valor da Condenação
                </label>
                <input
                  type="text"
                  name="honorários_s_valor_da_condenação"
                  value={formData.honorários_s_valor_da_condenação}
                  onChange={handleChange}
                  required
                  placeholder="Ex: 10%"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Honorários Valor Fixo */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Honorários em Valor Fixo
                </label>
                <input
                  type="number"
                  name="honorários_em_valor_fixo"
                  value={formData.honorários_em_valor_fixo}
                  onChange={handleChange}
                  required
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Deságio Principal */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Deságio a Aplicar sobre o Principal (%)
                </label>
                <input
                  type="number"
                  name="deságio_a_aplicar_sobre_o_principal"
                  value={formData.deságio_a_aplicar_sobre_o_principal}
                  onChange={handleChange}
                  required
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Deságio Honorários */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Deságio a Aplicar em Honorários (%)
                </label>
                <input
                  type="number"
                  name="deságio_em_a_aplicar_em_honorários"
                  value={formData.deságio_em_a_aplicar_em_honorários}
                  onChange={handleChange}
                  required
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Botão Submit */}
            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Calculando...' : 'Calcular'}
              </button>
            </div>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">
                  {error}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        {/* Results */}
        {results && !loading && (
          <ResultTable results={results} />
        )}
      </div>
    </div>
  );
}

export default App;
