# Script para iniciar Backend + Ngrok automaticamente
# Uso: .\start-ngrok.ps1

Write-Host "🚀 Iniciando ServFaz MVP com Ngrok..." -ForegroundColor Cyan
Write-Host ""

# Verificar se Ngrok está configurado
Write-Host "1️⃣ Verificando Ngrok..." -ForegroundColor Yellow
$ngrokPath = "$env:USERPROFILE\ngrok\ngrok.exe"

if (!(Test-Path $ngrokPath)) {
    Write-Host "❌ Ngrok não encontrado em $ngrokPath" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Ngrok encontrado!" -ForegroundColor Green
Write-Host ""

# Verificar se backend está rodando
Write-Host "2️⃣ Verificando Backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Backend já está rodando!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Backend não está rodando." -ForegroundColor Yellow
    Write-Host "   Por favor, inicie o backend em outro terminal:" -ForegroundColor Yellow
    Write-Host "   cd backend; python main.py" -ForegroundColor White
    Write-Host ""
    $continuar = Read-Host "Continuar mesmo assim? (s/n)"
    if ($continuar -ne 's') {
        exit 0
    }
}

Write-Host ""

# Iniciar Ngrok
Write-Host "3️⃣ Iniciando túnel Ngrok..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🔗 URL pública será mostrada abaixo:" -ForegroundColor Cyan
Write-Host "   Copie a URL 'Forwarding' e atualize frontend\.env.local" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Para parar: Ctrl+C" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor DarkGray

# Executar Ngrok (fica em execução)
& $ngrokPath http 8000
