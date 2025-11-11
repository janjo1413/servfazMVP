// Configuração da URL base da API
// Em desenvolvimento: usa proxy do Vite (/api -> http://localhost:8000)
// Em produção: usa variável de ambiente VITE_API_URL
export const API_BASE_URL = import.meta.env.VITE_API_URL || '';

// Helper para construir URLs da API
export const getApiUrl = (endpoint) => {
  // Se tiver VITE_API_URL configurado, usa diretamente
  if (import.meta.env.VITE_API_URL) {
    return `${import.meta.env.VITE_API_URL}${endpoint}`;
  }
  // Caso contrário, usa o proxy do Vite (/api)
  return `/api${endpoint}`;
};
