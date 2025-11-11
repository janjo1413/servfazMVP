// Configuração da URL base da API
// Em desenvolvimento: usa proxy do Vite (/api -> http://localhost:8000)
// Em produção: usa variável de ambiente VITE_API_URL

// Fallback hardcoded (temporário para testes)
const DEFAULT_API_URL = 'https://nixon-actinoid-faustino.ngrok-free.dev';

export const API_BASE_URL = import.meta.env.VITE_API_URL || DEFAULT_API_URL;

// Headers padrão para bypass do aviso do Ngrok
export const getDefaultHeaders = () => ({
  'Content-Type': 'application/json',
  'ngrok-skip-browser-warning': 'true',
});

// Helper para construir URLs da API
export const getApiUrl = (endpoint) => {
  // Tenta pegar da variável de ambiente primeiro
  const apiUrl = import.meta.env.VITE_API_URL;
  
  if (apiUrl) {
    console.log('🔗 Usando API URL (env):', apiUrl);
    return `${apiUrl}${endpoint}`;
  }
  
  // Se estiver em produção (Vercel) e não tiver env, usa fallback
  if (import.meta.env.PROD) {
    console.log('🔗 Usando API URL (fallback):', DEFAULT_API_URL);
    return `${DEFAULT_API_URL}${endpoint}`;
  }
  
  // Desenvolvimento: usa proxy do Vite (/api)
  console.log('🔗 Usando proxy local:', `/api${endpoint}`);
  return `/api${endpoint}`;
};
