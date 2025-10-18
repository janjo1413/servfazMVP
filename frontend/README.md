# Frontend - ServFaz MVP

## 📝 Descrição

Interface React moderna que permite o usuário inserir dados de processos jurídicos e visualizar os resultados calculados pelo Excel.

## 🎯 Propósito

Este módulo é responsável por:
- Renderizar formulário dinâmico baseado em `schema_input.json`
- Enviar dados para o backend via `POST /calculate`
- Exibir resultados das tabelas vermelhas
- Destacar "TOTAL DO VALOR PROPOSTO PARA ACORDO"
- Proporcionar experiência de usuário limpa e responsiva

## 📁 Estrutura

```
frontend/
├── src/
│   ├── App.jsx              # Componente principal com formulário
│   ├── main.jsx             # Entry point do React
│   ├── index.css            # Estilos globais (Tailwind)
│   └── components/
│       └── ResultTable.jsx  # Componente de exibição de resultados
├── public/                  # Arquivos estáticos
├── index.html               # HTML base
├── package.json             # Dependências npm
├── vite.config.js           # Configuração do Vite
├── tailwind.config.js       # Configuração do Tailwind
└── postcss.config.js        # Configuração do PostCSS
```

## 🔧 Componentes e Funções

### `App.jsx`
**Propósito:** Componente principal que gerencia estado e formulário

**Estado:**
- `formData` - Dados do formulário (10 campos do schema_input.json)
- `results` - Resultados retornados pelo backend
- `loading` - Indicador de carregamento
- `error` - Mensagens de erro

**Fluxo:**
1. Usuário preenche formulário
2. Submit → `POST /api/calculate`
3. Aguarda resposta do backend
4. Renderiza `ResultTable` com resultados
5. Ou exibe erro se houver falha

**Decisões técnicas:**
- Validação HTML5 nativa (`required`)
- Fetch API para requisições
- Proxy Vite para `/api` → backend
- Estados separados para loading/error/results

### `components/ResultTable.jsx`
**Propósito:** Renderiza as tabelas de resultados

**Funcionalidades:**
- Formatação de números (pt-BR, 2 decimais)
- Detecção automática de "TOTAL DO VALOR PROPOSTO PARA ACORDO"
- Destaque visual (borda verde) para bloco especial
- Preenchimento de células vazias quando total tem menos colunas
- Botão "Nova Consulta" para resetar

**Decisões técnicas:**
- Componente funcional com React Hooks
- Tailwind para estilização
- Tabelas responsivas com overflow-x-auto
- Formatação condicional (verde para acordo)

## 🚀 Como Executar

### Instalação de dependências:
```powershell
cd frontend
npm install
```

### Executar em desenvolvimento:
```powershell
npm run dev
```

Acesse: http://localhost:3000

### Build para produção:
```powershell
npm run build
```

### Preview da build:
```powershell
npm run preview
```

## 🎨 Tecnologias Utilizadas

- **React 18** - Framework UI
- **Vite** - Build tool e dev server
- **TailwindCSS** - Estilização utilitária
- **PostCSS** - Processamento CSS
- **Fetch API** - Requisições HTTP

## 🔌 Integração com Backend

### Configuração de Proxy (vite.config.js)
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

**Exemplo de requisição:**
```javascript
fetch('/api/calculate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(formData)
})
```

## 📋 Campos do Formulário

| Campo | Tipo | Descrição |
|-------|------|-----------|
| município | text | Nome do município |
| ajuizamento | text | Data de ajuizamento (DD/MM/AAAA) |
| citação | text | Data de citação |
| início_cálculo | text | Data de início do cálculo |
| final_cálculo | text | Data final do cálculo |
| correção_até | text | Data de correção |
| honorários_s_valor_da_condenação | text | Percentual (ex: 10%) |
| honorários_em_valor_fixo | number | Valor fixo |
| deságio_a_aplicar_sobre_o_principal | number | Percentual (0-100) |
| deságio_em_a_aplicar_em_honorários | number | Percentual (0-100) |

## 🎨 Design System

### Cores
- **Primária:** Azul (`blue-600`)
- **Sucesso:** Verde (`green-500`) - Para acordo
- **Erro:** Vermelho (`red-500`)
- **Neutro:** Cinza (`gray-50` a `gray-900`)

### Componentes
- **Formulário:** Cards brancos com sombra
- **Tabelas:** Layout responsivo com hover
- **Botões:** Estados hover e disabled
- **Alertas:** Border-left colorido

## 🔄 Histórico de Alterações

### v1.0.0 - 2025-10-17
- ✅ Estrutura inicial do frontend
- ✅ Formulário completo com 10 campos
- ✅ Componente de resultados
- ✅ Destaque para bloco de acordo
- ✅ Formatação de valores pt-BR
- ✅ Tratamento de erros
- ✅ Loading states

## ⚠️ Observações Importantes

1. **Backend deve estar rodando** em http://127.0.0.1:8000
2. Proxy do Vite redireciona `/api/*` para o backend
3. Validação básica via HTML5 (melhorias futuras)
4. Design responsivo (mobile-first)

## 🔜 Próximas Melhorias

- [ ] Validação de datas com biblioteca (date-fns)
- [ ] Máscaras de input (react-input-mask)
- [ ] Exportação de resultados (PDF/Excel)
- [ ] Histórico de consultas
- [ ] Gráficos visuais
- [ ] Testes unitários (Vitest)
- [ ] Acessibilidade (ARIA labels)
