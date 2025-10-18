# Backend - ServFaz MVP

## 📝 Descrição

Backend FastAPI que utiliza **Excel como motor de cálculo** para processos jurídicos.

## 🎯 Propósito

Este módulo é responsável por:
- Receber dados do frontend via API REST
- Escrever dados na planilha Excel (`planilhamae.xlsx`)
- Executar cálculos via xlwings
- Ler resultados das tabelas vermelhas (linhas 21-104)
- Persistir dados no SQLite
- Retornar resultados estruturados em JSON

## 📁 Estrutura

```
backend/
├── main.py              # API FastAPI com endpoint /calculate
├── database.py          # Inicialização do banco SQLite
└── services/
    ├── excel_runner.py  # Integração com Excel via xlwings
    ├── selic_api.py     # Integração com API do Banco Central
    └── storage.py       # Persistência no SQLite
```

## 🔧 Arquivos e Funções

### `main.py`
**Propósito:** API principal com endpoints REST

**Endpoints:**
- `POST /calculate` - Processa cálculo completo
- `GET /results/{id}` - Recupera resultado por ID
- `GET /results` - Lista últimos resultados

**Fluxo do `/calculate`:**
1. Recebe JSON (schema_input.json)
2. Valida SELIC para data de correção
3. Escreve na aba "RESUMO" (células B6-B15)
4. Executa `app.calculate()`
5. Lê tabelas (A-F + AB, linhas 21-104)
6. Salva no SQLite
7. Retorna JSON (schema_output.json)

### `services/excel_runner.py`
**Propósito:** Gerencia interação com Excel

**Decisões técnicas:**
- Context manager (`with`) para garantir fechamento do Excel
- xlwings em modo invisível (`visible=False`)
- Leitura linha a linha para identificar blocos
- Tratamento especial para "TOTAL DO VALOR PROPOSTO PARA ACORDO" (apenas A-C)

**Métodos principais:**
- `write_inputs()` - Escreve dados nas células
- `calculate()` - Executa recálculo da planilha
- `read_results()` - Lê tabelas estruturadas

### `services/selic_api.py`
**Propósito:** Integração com API do Banco Central

**Decisões técnicas:**
- Cache local em `data/selic_cache.json`
- Requisição sob demanda (apenas se mês não existir)
- API oficial: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json`

**Métodos principais:**
- `ensure_selic()` - Garante disponibilidade do mês
- `fetch_selic_data()` - Busca dados da API
- `_save_cache()` - Persiste cache localmente

### `services/storage.py`
**Propósito:** Persistência de dados no SQLite

**Decisões técnicas:**
- Tabela única `results` com JSON serializado
- UUID para IDs únicos
- Timestamp UTC para created_at

**Métodos principais:**
- `save_result()` - Salva input + output
- `get_result()` - Recupera por ID
- `list_results()` - Lista últimos registros

### `database.py`
**Propósito:** Inicialização do banco

**Decisões técnicas:**
- Criação automática de tabelas no startup
- Path configurável via variável de ambiente

## 🚀 Como Executar

### Instalação de dependências:
```powershell
pip install fastapi uvicorn xlwings httpx python-dotenv openpyxl
```

### Executar servidor:
```powershell
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Testar API:
```powershell
# Health check
curl http://localhost:8000

# Documentação interativa
# Abrir no navegador: http://localhost:8000/docs
```

## 📊 Mapa de Células (RESUMO)

| Campo | Célula |
|-------|--------|
| município | B6 |
| ajuizamento | B7 |
| citação | B8 |
| início_cálculo | B9 |
| final_cálculo | B10 |
| honorários_s_valor_da_condenação | B11 |
| honorários_em_valor_fixo | B12 |
| deságio_a_aplicar_sobre_o_principal | B13 |
| deságio_em_a_aplicar_em_honorários | B14 |
| correção_até | B15 |

## 📖 Leitura das Tabelas

**Intervalo:** Linhas 21-104  
**Colunas:** A-F + AB

**Estrutura de cada bloco:**
- Linha N: Título (coluna A)
- Linha N+1: Cabeçalho (A-F)
- Linha N+2: Valores (A-F)
- Linha N+3: Total (A-C ou A-F)
- Linha N+4: Espaçamento vazio

**Regra especial:**
"TOTAL DO VALOR PROPOSTO PARA ACORDO" → apenas colunas A-C

## 🔄 Histórico de Alterações

### v1.0.0 - 2025-10-17
- ✅ Estrutura inicial do backend
- ✅ Endpoint /calculate completo
- ✅ Integração com xlwings
- ✅ Integração com API SELIC
- ✅ Persistência SQLite
- ✅ Tratamento de blocos especiais (ACORDO)

## ⚠️ Observações Importantes

1. **Excel deve estar instalado no Windows** para xlwings funcionar
2. Planilha `planilhamae.xlsx` deve existir em `/data`
3. Processo é **síncrono** - uma requisição por vez
4. Excel abre em modo invisível mas pode consumir recursos

## 🔜 Próximas Melhorias

- [ ] Processamento assíncrono (fila)
- [ ] Validação mais robusta de células
- [ ] Logs estruturados
- [ ] Testes unitários
- [ ] Cache de resultados
