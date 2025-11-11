#!/bin/bash
set -e

echo "=================================================="
echo "🚀 ServFaz MVP - Startup Script (Azure App Service)"
echo "=================================================="

# Verificar Python
echo "✓ Python version:"
python --version

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p /home/site/wwwroot/data
mkdir -p /home/site/wwwroot/logs
echo "✓ Diretórios criados"

# Verificar variáveis de ambiente críticas
echo "🔍 Verificando configuração..."
if [ -z "$EXCEL_FILE_PATH" ]; then
    echo "⚠️  EXCEL_FILE_PATH não configurado, usando default"
    export EXCEL_FILE_PATH=/home/site/wwwroot/data/planilhamae.xlsx
fi

echo "📋 Configuração atual:"
echo "  - ENVIRONMENT: $ENVIRONMENT"
echo "  - EXCEL_PATH: $EXCEL_FILE_PATH"
echo "  - DATABASE_URL: ${DATABASE_URL:0:20}..."
echo "  - LOG_LEVEL: $LOG_LEVEL"

# Verificar se planilha Excel existe
if [ -f "$EXCEL_FILE_PATH" ]; then
    echo "✓ Planilha Excel encontrada"
else
    echo "⚠️  Planilha Excel não encontrada em $EXCEL_FILE_PATH"
    echo "   Upload necessário via FTP/Kudu"
fi

# Inicializar banco de dados
echo "💾 Inicializando banco de dados..."
python -c "from database import init_database; init_database('/home/site/wwwroot/data/results.db')" || echo "⚠️ Erro ao inicializar DB (pode já existir)"

# Atualizar cache SELIC inicial (importante para primeira execução)
echo "📊 Atualizando cache SELIC..."
python -c "
try:
    from services.selic_api import SelicAPI
    api = SelicAPI('/home/site/wwwroot/data/selic_cache.json')
    api.update_cache()
    print('✓ Cache SELIC atualizado')
except Exception as e:
    print(f'⚠️  Erro ao atualizar SELIC: {str(e)}')
" || echo "⚠️ Falha na atualização inicial de SELIC (continuando...)"

# Configuração do Gunicorn
WORKERS=${GUNICORN_WORKERS:-4}
TIMEOUT=${GUNICORN_TIMEOUT:-120}
BIND_ADDRESS=${BIND_ADDRESS:-0.0.0.0:8000}

echo "=================================================="
echo "🟢 Iniciando Gunicorn com Uvicorn workers"
echo "  - Workers: $WORKERS"
echo "  - Timeout: $TIMEOUT segundos"
echo "  - Bind: $BIND_ADDRESS"
echo "=================================================="

# Iniciar aplicação com Gunicorn + Uvicorn
exec gunicorn main:app \
  --workers $WORKERS \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind $BIND_ADDRESS \
  --timeout $TIMEOUT \
  --access-logfile /home/site/wwwroot/logs/access.log \
  --error-logfile /home/site/wwwroot/logs/error.log \
  --log-level ${LOG_LEVEL:-info} \
  --preload \
  --forwarded-allow-ips="*"
