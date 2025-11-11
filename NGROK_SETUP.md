# 🚀 Guia Rápido Ngrok

## ✅ Instalação Completa
Ngrok instalado em: `C:\Users\jgque\ngrok\ngrok.exe`

## 📋 Próximos Passos

### 1. Configure o Authtoken
Acesse: https://dashboard.ngrok.com/get-started/your-authtoken

Execute no PowerShell:
```powershell
& "$env:USERPROFILE\ngrok\ngrok.exe" config add-authtoken SEU_TOKEN_AQUI
```

### 2. Inicie o Backend
```powershell
cd backend
python main.py
```

### 3. Crie o Túnel Ngrok
Em outro terminal PowerShell:
```powershell
& "$env:USERPROFILE\ngrok\ngrok.exe" http 8000
```

Você verá algo como:
```
Forwarding: https://abc123.ngrok-free.app -> http://localhost:8000
```

### 4. Configure o Frontend
Edite `frontend\.env.local`:
```env
VITE_API_URL=https://abc123.ngrok-free.app
```

### 5. Inicie o Frontend
```powershell
cd frontend
npm run dev
```

### 6. Acesse
- **Local**: http://localhost:3000
- **Ngrok**: Use a URL do túnel Ngrok
- **API**: https://abc123.ngrok-free.app

## 🔧 Comandos Úteis

### Verificar instalação
```powershell
& "$env:USERPROFILE\ngrok\ngrok.exe" version
```

### Parar o túnel
`Ctrl + C` no terminal do Ngrok

### Ver túneis ativos
```powershell
& "$env:USERPROFILE\ngrok\ngrok.exe" tunnels list
```

## ⚠️ Notas Importantes
- **CORS**: Já configurado no backend (`allow_origins=["*"]`)
- **URL muda**: Cada vez que reiniciar o Ngrok, a URL muda (plano gratuito)
- **Timeout**: Conexões ficam abertas por 2h (plano gratuito)
- **Banner**: Visitantes verão um banner de aviso do Ngrok

## 🎯 Testando
1. Acesse: `https://SEU-NGROK-URL.ngrok-free.app/`
2. Deve retornar: `{"status":"online","service":"RcJgJp MVP",...}`
