# 🚀 GUIA RÁPIDO - VALIDAÇÃO MANUAL DE SELIC

## ⚡ **MÉTODO RÁPIDO (5 minutos)**

### **1. COPIAR VALORES DO SISTEMA:**
```
Resultados Base (01/01/2025):
- Coluna D: R$ 2.500.000,00  ← COPIE ESTE

Resultados Atualizados (01/03/2025):
- Coluna D: R$ 2.548.998,00  ← COPIE ESTE
```

### **2. COPIAR TAXAS SELIC:**
Abra: `data/selic_cache.json`
```json
"2025-02": 0.99,
"2025-03": 0.96
```

### **3. CALCULAR NA CALCULADORA:**
```
2.500.000,00 × 1,0099 = 2.524.750,00
2.524.750,00 × 1,0096 = 2.548.998,00
```

### **4. COMPARAR:**
```
Calculado: R$ 2.548.998,00
Sistema:   R$ 2.548.998,00
Resultado: ✅ BATE!
```

---

## 🧮 **FÓRMULA RÁPIDA:**

```
Valor Final = Valor Base × (1 + SELIC1/100) × (1 + SELIC2/100) × ...
```

**Exemplo:**
- Base: R$ 1.000.000
- SELIC fev: 0.99% → fator = 1,0099
- SELIC mar: 0.96% → fator = 1,0096

**Cálculo:**
```
1.000.000 × 1,0099 × 1,0096 = 1.019.594,04
```

---

## 📱 **COM CALCULADORA DO CELULAR:**

1. Digite: `2500000`
2. Aperte: `×`
3. Digite: `1.0099`
4. Aperte: `=` → Resultado: 2.524.750
5. Aperte: `×`
6. Digite: `1.0096`
7. Aperte: `=` → Resultado: 2.548.998

---

## 💻 **COM EXCEL:**

```
A1: =2500000
A2: =A1*1.0099
A3: =A2*1.0096
```

Resultado em A3: **2.548.998**

---

## 🐍 **COM PYTHON (Script Automático):**

1. Edite: `tests/validacao_manual_selic_calculadora.py`
2. Altere as 3 linhas no topo:
   ```python
   VALOR_BASE = 2_500_000.00      # ← SEU VALOR
   DATA_CORRECAO = "01/03/2025"   # ← SUA DATA
   VALOR_SISTEMA = 2_548_998.00   # ← VALOR DO SISTEMA
   ```
3. Execute:
   ```bash
   cd tests
   python validacao_manual_selic_calculadora.py
   ```

---

## ✅ **CHECKLIST RÁPIDO:**

- [ ] Copiei valor base (Coluna D)
- [ ] Copiei valor do sistema (Coluna D atualizada)
- [ ] Peguei taxas SELIC no `selic_cache.json`
- [ ] Calculei: Base × (1 + 0.99/100) × (1 + 0.96/100) × ...
- [ ] Comparei: Diferença < R$ 0,10 = ✅ CORRETO

---

## 🎯 **EXEMPLO COMPLETO:**

| Item | Valor |
|------|-------|
| Valor Base | R$ 1.000.000,00 |
| SELIC fev/25 | 0.99% |
| SELIC mar/25 | 0.96% |
| **Cálculo** | 1.000.000 × 1.0099 × 1.0096 |
| **Resultado** | R$ 1.019.594,04 |
| Sistema retornou | R$ 1.019.594,04 |
| **Validação** | ✅ CORRETO! |

---

## 📚 **DOCUMENTOS RELACIONADOS:**

- 📖 **Guia Completo**: `VALIDACAO_MANUAL_SELIC.md`
- 🐍 **Script Python**: `validacao_manual_selic_calculadora.py`
- 🧪 **Testes Automatizados**: `validacao_selic.py`
- 📋 **Instruções Manuais**: `INSTRUCOES_TESTE_MANUAL.md`

---

## 💡 **DICA DE OURO:**

**Se a diferença for < R$ 0,10** → Sistema está **CORRETO!**  
*(Pequenas diferenças são normais devido a arredondamentos)*

---

**Pronto para validar! 🚀**
