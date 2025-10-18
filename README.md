# ServFaz MVP - Sistema de Cálculo Jurídico

## 🎯 Visão Geral

Sistema web completo (FastAPI + React) que utiliza **Excel como motor de cálculo** para processos jurídicos do FUNDEF.

O usuário preenche um formulário web, os dados são escritos automaticamente na planilha `planilhamae.xlsx`, o Excel executa os cálculos complexos, e os resultados são exibidos instantaneamente na interface.

## ✨ Funcionalidades

- ✅ **Formulário Web Intuitivo**: 10 campos incluindo datas, honorários e deságios
- ✅ **Integração Completa com Excel**: Escrita/leitura via xlwings mantendo todas as fórmulas ativas
- ✅ **Validação Automática de SELIC**: Consulta API do Banco Central com cache local
- ✅ **17 Tabelas de Resultados**: Diferentes metodologias de cálculo (NT7, NT36, IASA, etc.)
- ✅ **Persistência em SQLite**: Histórico completo de todos os cálculos
- ✅ **Interface Responsiva**: React + TailwindCSS com formatação pt-BR

## 🔄 Fluxo de Dados

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   FRONTEND  │─────▶│   BACKEND   │─────▶│    EXCEL    │─────▶│   SQLITE    │
│   (React)   │      │  (FastAPI)  │      │ (xlwings)   │      │  (Storage)  │
│             │      │             │      │             │      │             │
│  - Form     │      │  - Validação│      │  - Fórmulas │      │  - Histórico│
│  - Tabelas  │      │  - SELIC API│      │  - Cálculos │      │  - Consulta │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
      ▲                                            │
      │                                            │
      └────────────────────────────────────────────┘
                   Resultados (JSON)
```

## 📁 Estrutura do Projeto

```
servfazMVP/
│
├── backend/                    # API FastAPI
│   ├── main.py                 # Endpoints principais
│   ├── database.py             # Configuração SQLite
│   └── services/
│       ├── excel_runner.py     # Integração xlwings
│       ├── selic_api.py        # Consulta Banco Central
│       └── storage.py          # Persistência de dados
│
├── frontend/                   # Interface React + Vite
│   ├── src/
│   │   ├── App.jsx             # Formulário e lógica principal
│   │   └── components/
│   │       └── ResultTable.jsx # Exibição de resultados
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   ├── planilhamae.xlsx        # Excel com fórmulas de cálculo
│   ├── mapa_celulas.json       # Mapeamento de campos → células
│   ├── schema_input.json       # Schema de entrada
│   └── schema_output.json      # Schema de saída
│
├── scripts/
│   └── gen_schema_from_excel.py # Geração de schemas
│
└── .gitignore
```

## 🚀 Como Executar

### Pré-requisitos

- **Python 3.13+** com pip
- **Node.js 18+** com npm
- **Microsoft Excel** (Windows com xlwings)

### 1. Instalar Dependências

**Backend:**
```powershell
cd backend
pip install fastapi uvicorn xlwings httpx openpyxl python-dotenv
```

**Frontend:**
```powershell
cd frontend
npm install
```

### 2. Iniciar Servidores

**Terminal 1 - Backend:**
```powershell
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### 3. Acessar

- **Frontend**: http://localhost:3000
- **API Docs**: http://127.0.0.1:8000/docs

## 📊 Mapeamento de Dados

### Entrada (cells B6-B15)
| Campo | Célula | Tipo |
|-------|--------|------|
| Município | B6 | texto |
| Data de Ajuizamento | B7 | data |
| Data de Citação | B8 | data |
| Início do Cálculo | B9/E6 | data |
| Final do Cálculo | B10/F6 | data |
| Honorários % | B11 | percentual |
| Honorários Fixo | B12 | moeda |
| Deságio Principal | B13 | percentual |
| Deságio Honorários | B14 | percentual |
| Correção Até | B15 | data |

### Saída (linhas 21-104)
- **17 blocos** de tabelas com diferentes metodologias
- **Colunas**: A-F (Descrição, Valores, Juros, Atualizado, Honorários) + AB
- **Linha especial**: "TOTAL DO VALOR PROPOSTO PARA ACORDO"

## 🔧 Detalhes Técnicos

### Conversões Críticas

**Datas**: Strings DD/MM/YYYY são convertidas para `datetime` antes de escrever no Excel para evitar ambiguidade de formato.

**Percentuais**: Células B11, B13, B14 estão formatadas como `%` no Excel. O sistema divide valores por 100 antes de escrever:
- Usuário digita: `20`
- Sistema escreve: `0.20`
- Excel exibe: `20%`

**Leitura**: Células formatadas como `%` são detectadas e valores são divididos por 100 ao ler para evitar valores 100x maiores.

### API SELIC

- **Endpoint**: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados`
- **Cache**: `data/selic_cache.json` (revalidação diária)
- **Validação**: Data de correção deve ter SELIC disponível

### Banco de Dados

**Tabela `results`**:
```sql
CREATE TABLE results (
    id TEXT PRIMARY KEY,
    created_at TEXT,
    input_data TEXT,  -- JSON
    output_data TEXT  -- JSON
)
```

## 🐛 Troubleshooting

### Excel não abre
- Verifique se Microsoft Excel está instalado
- Execute como Administrador se necessário
- Desative proteções/macros que bloqueiem xlwings

### Valores negativos ou incorretos
- Confirme que datas estão em formato DD/MM/YYYY
- Verifique se SELIC está disponível para data de correção
- Confira se planilha não tem erros nas fórmulas

### Erro "Port already in use"
- Backend: mude porta em `uvicorn main:app --port 8001`
- Frontend: Vite automaticamente tenta portas alternativas

### Valores 100x maiores (Honorários)
- Verifique se tipo do campo é `float` no Pydantic model
- Confirme que conversão de percentuais está ativa

## 📝 Endpoints da API

### `POST /calculate`
**Request:**
```json
{
  "município": "TIMON",
  "ajuizamento": "01/05/2005",
  "citação": "01/06/2006",
  "início_cálculo": "01/01/2000",
  "final_cálculo": "01/12/2006",
  "honorários_s_valor_da_condenação": 20,
  "honorários_em_valor_fixo": 5000,
  "deságio_a_aplicar_sobre_o_principal": 20,
  "deságio_em_a_aplicar_em_honorários": 20,
  "correção_até": "01/01/2025"
}
```

**Response:**
```json
{
  "id": "uuid-do-calculo",
  "created_at": "2025-10-18T17:00:00",
  "results": [
    {
      "titulo": "NT7 (IPCA + 0,5% até 12/2002...)",
      "header": ["Descrição", "Valor Corrigido Mensal", ...],
      "rows": [[...], [...]],
      "total": [...]
    }
  ]
}
```

### `GET /results/{id}`
Busca cálculo específico por ID.

### `GET /results`
Lista todos os cálculos salvos.

## 🎨 Frontend

### Componentes

**`App.jsx`**:
- Formulário com validação
- Estado de loading/erro
- Chamada à API
- Renderização de resultados

**`ResultTable.jsx`**:
- Formatação pt-BR (R$ 1.234,56)
- Destaque especial para blocos ACORDO
- Suporte a 7 colunas (A-F + AB)

### Estilização

- **TailwindCSS 3.4**: Utility-first CSS
- **Tema escuro**: bg-gray-900, text-white
- **Cores**: Blue-500 (botões), Green-500 (destaque ACORDO)

## 📦 Dependências

### Backend
```txt
fastapi==0.116.0
uvicorn[standard]
xlwings
httpx
openpyxl
python-dotenv
```

### Frontend
```json
{
  "react": "^18.3.1",
  "vite": "^6.4.0",
  "tailwindcss": "^3.4.17",
  "postcss": "^8.5.1",
  "autoprefixer": "^10.4.21"
}
```

## 🔐 Segurança

- ⚠️ **MVP apenas**: Sem autenticação implementada
- ⚠️ **Excel local**: Não executar em produção com múltiplos usuários simultâneos
- ⚠️ **Sem validação avançada**: Input sanitization básica apenas

## 🚧 Limitações Conhecidas

- **Excel deve estar instalado localmente** (Windows)
- **Um cálculo por vez** (xlwings não suporta paralelização)
- **Sem tratamento de erros do Excel** (fórmulas quebradas causam crash)
- **Cache SELIC não expira automaticamente** (limpeza manual necessária)

## 📄 Licença

Este é um projeto MVP para fins educacionais/demonstração.

## 👨‍💻 Autor

Desenvolvido para automatizar cálculos jurídicos complexos de FUNDEF, substituindo processo manual em Excel por interface web integrada.
