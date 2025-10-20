# Funcionalidade de Atualização SELIC

## 📋 Resumo

O sistema agora possui **duas camadas de resultados**:

1. **Resultados Base (01/01/2025)**: Valores fixos da planilha Excel
2. **Resultados Atualizados com SELIC**: Valores atualizados mensalmente com a taxa SELIC (apenas para datas > 01/01/2025)

---

## 🎯 Como Funciona

### Campo "Correção Até"

Este campo agora é **funcional** e determina se haverá atualização SELIC:

- **Data ≤ 01/01/2025**: Mostra apenas os resultados base da planilha
- **Data > 01/01/2025**: Mostra os resultados base **+** resultados atualizados com SELIC

### Exemplo Prático

**Usuário insere:** `01/03/2025`

**Sistema executa:**
1. Lê os valores da planilha (base 01/01/2025)
2. Identifica que 01/03/2025 > 01/01/2025
3. Aplica SELIC de fevereiro/2025
4. Aplica SELIC de março/2025
5. Mostra **duas seções**:
   - 📊 Resultados Base (01/01/2025)
   - 🔄 Resultados Atualizados com SELIC (até 01/03/2025)

---

## 📊 Tabelas Afetadas

**Todas as 17 tabelas** são atualizadas, incluindo:

1. NT7 (IPCA + SELIC)
2. NT7 (COM ANATOCISMO - MÉTODO CNJ)
3. NT36 (IPCA + SELIC)
4. JASA (IPCA + SELIC)
5. NT7 TR
6. NT36 TR
7. JASA TR
8. NT7 IPCA-E
9. NT36 IPCA-E
10. NT36 IPCA-E + Juros 1%
11. JASA IPCA-E
12. NT7 SELIC
13. NT36 SELIC
14. JASA SELIC
15. NT7 IPCA-E + Juros 1% (COM Anatocismo)
16. NT7 IPCA-E + Juros 1% (SEM Anatocismo)
17. NT36 IPCA-E + Juros 1% (SEM Anatocismo)

---

## 🔢 Colunas Atualizadas

Para cada tabela, as seguintes colunas são atualizadas:

- **Coluna C**: Valor dos Juros Mensal
- **Coluna D**: Valor Atualizado
- **Coluna E**: Honorários

**Fórmula de atualização:**
```
valor_atualizado = valor_base × (1 + SELIC_fev/100) × (1 + SELIC_mar/100) × ...
```

---

## 💾 Cache SELIC

O sistema utiliza um cache local de taxas SELIC mensais:

- **Arquivo**: `data/selic_cache.json`
- **Fonte**: API do Banco Central
- **Atualizado até**: Outubro/2025
- **Formato**: `{ "YYYY-MM": valor_percentual }`

Exemplo:
```json
{
  "2025-01": 1.01,
  "2025-02": 0.99,
  "2025-03": 0.96
}
```

---

## 🏗️ Arquitetura da Solução

### Backend

#### Novos Arquivos
- `backend/services/selic_updater.py`: Serviço de atualização SELIC

#### Arquivos Modificados
- `backend/main.py`: Endpoint `/calculate` atualizado

### Frontend

#### Arquivos Modificados
- `frontend/src/components/ResultTable.jsx`: Renderiza duas seções de resultados
- `frontend/src/App.jsx`: Hint no campo "Correção Até"

### Scripts

#### Novos Scripts
- `scripts/identify_selic_cells.py`: Análise de dependências SELIC na planilha

### Dados

#### Novos Arquivos
- `data/selic_mapping.json`: Mapeamento de células/tabelas que usam SELIC

---

## 🔍 Fluxo de Dados

```
┌──────────────────────────────────────────────────────────────┐
│ 1. Usuário preenche formulário + "Correção Até"             │
└──────────────────────┬───────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. Backend: Executa cálculo Excel (base 01/01/2025)         │
└──────────────────────┬───────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. Backend: Lê 17 tabelas da planilha                       │
└──────────────────────┬───────────────────────────────────────┘
                       ▼
              ┌────────┴────────┐
              │ Data > 01/01/25? │
              └────────┬─────────┘
                   Sim │         │ Não
          ┌────────────┘         └──────────┐
          ▼                                 ▼
┌─────────────────────────┐    ┌────────────────────────┐
│ 4a. Aplica SELIC mensal │    │ 4b. Pula atualização   │
│     (fev, mar, ...)     │    └────────┬───────────────┘
└──────────┬──────────────┘             │
           │                            │
           └──────────┬─────────────────┘
                      ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. Frontend: Mostra Resultados Base                         │
│            + Resultados Atualizados (se houver)              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testando

### Teste 1: Data ≤ 01/01/2025

**Input:**
- Correção até: `01/01/2025`

**Resultado Esperado:**
- ✅ Mostra apenas "Resultados Base (01/01/2025)"
- ❌ Não mostra seção "Resultados Atualizados"

### Teste 2: Data > 01/01/2025

**Input:**
- Correção até: `01/03/2025`

**Resultado Esperado:**
- ✅ Mostra "Resultados Base (01/01/2025)"
- ✅ Mostra "Resultados Atualizados com SELIC (até 01/03/2025)"
- ✅ Valores da seção atualizada são maiores (devido à SELIC aplicada)

### Teste 3: Data muito futura

**Input:**
- Correção até: `01/12/2025`

**Resultado Esperado:**
- ✅ Sistema busca SELIC de fev a dez/2025 no cache
- ✅ Aplica todas as taxas mensais progressivamente

---

## 🚀 Executando

### Backend
```powershell
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend
```powershell
cd frontend
npm run dev
```

### Acessar
- Frontend: http://localhost:3000
- API Docs: http://127.0.0.1:8000/docs

---

## 📝 Notas Técnicas

1. **Precisão**: A SELIC é aplicada de forma composta (juros sobre juros)
2. **Performance**: O cache local evita chamadas repetidas à API do Banco Central
3. **Escalabilidade**: Novas taxas SELIC podem ser adicionadas manualmente ao `selic_cache.json`
4. **Retrocompatibilidade**: Resultados antigos salvos no banco continuam válidos

---

## 🔮 Próximos Passos (Opcional)

- [ ] Atualização automática do cache SELIC via scheduler
- [ ] Comparação visual (gráfico) entre resultados base e atualizados
- [ ] Exportação para PDF com ambas as seções
- [ ] Histórico de taxas SELIC aplicadas por cálculo
