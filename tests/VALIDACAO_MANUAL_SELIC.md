# 📐 VALIDAÇÃO MANUAL DE CÁLCULOS SELIC

Este guia ensina como **validar manualmente** se o sistema está aplicando SELIC corretamente.

---

## 🎯 **O QUE VOCÊ VAI FAZER:**

1. Pegar um valor **base** (01/01/2025) da planilha
2. Aplicar SELIC **mês a mês** manualmente
3. Comparar com o valor que o sistema retornou
4. Se bater = ✅ Sistema correto!

---

## 📋 **PASSO 1: OBTER OS DADOS**

### **1.1 - Fazer um cálculo no sistema:**
- Acesse: http://localhost:5173
- Preencha o formulário:
  - **Município**: (escolha um que funciona)
  - **Data de correção**: Por exemplo, **01/03/2025**
  - Preencha os outros campos normalmente
- Clique em "Gerar Cálculo"

### **1.2 - Na tela de resultados, procure uma tabela:**
Exemplo: **"NT7 SELIC (SELIC desde quando devido até hoje)"**

Você verá **duas seções**:
- ✅ **Resultados Base (01/01/2025)** ← PEGAR DAQUI
- ✅ **Resultados Atualizados com SELIC (até 01/03/2025)** ← COMPARAR COM ESTE

### **1.3 - Anotar os valores:**

Na seção **"Resultados Base"**, procure a linha de **TOTAL**:

```
TOTAL DO VALOR PROPOSTO PARA ACORDO
- Coluna C (Juros): R$ 150.000,00        ← ANOTE ESTE
- Coluna D (Valor Atualizado): R$ 2.500.000,00  ← ANOTE ESTE
- Coluna E (Honorários): R$ 250.000,00   ← ANOTE ESTE
```

Na seção **"Resultados Atualizados"**, na mesma linha de TOTAL:

```
TOTAL DO VALOR PROPOSTO PARA ACORDO - ATUALIZADO ATÉ 01/03/2025
- Coluna C (Juros): R$ 155.280,50        ← ANOTE ESTE
- Coluna D (Valor Atualizado): R$ 2.585.280,50  ← ANOTE ESTE
- Coluna E (Honorários): R$ 258.528,05   ← ANOTE ESTE
```

---

## 🧮 **PASSO 2: BUSCAR AS TAXAS SELIC**

Acesse o arquivo: `data/selic_cache.json`

Procure os meses entre **01/01/2025** e sua **data de correção**:

**Exemplo**: Se correção é **01/03/2025**, você precisa de:
- `"2025-02"`: SELIC de fevereiro/2025
- `"2025-03"`: SELIC de março/2025

No arquivo você vai encontrar algo como:
```json
{
  "2025-02": 0.99,
  "2025-03": 0.96
}
```

**ANOTE ESTAS TAXAS!**

---

## 🔢 **PASSO 3: CALCULAR MANUALMENTE**

### **Fórmula da SELIC Composta:**

```
Valor Final = Valor Base × (1 + SELIC_mês1/100) × (1 + SELIC_mês2/100) × ...
```

---

### **EXEMPLO PRÁTICO:**

**Dados obtidos:**
- Valor Base (Coluna D): R$ **2.500.000,00**
- Data de correção: **01/03/2025**
- SELIC fevereiro/2025: **0.99%**
- SELIC março/2025: **0.96%**

**Cálculo:**

1. **Converter taxas para decimal:**
   - Fevereiro: 0.99% → 0.99 / 100 = **0.0099**
   - Março: 0.96% → 0.96 / 100 = **0.0096**

2. **Aplicar fevereiro/2025:**
   ```
   Valor após fev = 2.500.000,00 × (1 + 0.0099)
   Valor após fev = 2.500.000,00 × 1.0099
   Valor após fev = 2.524.750,00
   ```

3. **Aplicar março/2025:**
   ```
   Valor após mar = 2.524.750,00 × (1 + 0.0096)
   Valor após mar = 2.524.750,00 × 1.0096
   Valor após mar = 2.548.998,00
   ```

4. **Valor Final Esperado:** R$ **2.548.998,00**

---

## ✅ **PASSO 4: COMPARAR**

**Valor que você calculou:** R$ 2.548.998,00  
**Valor do sistema (Resultados Atualizados):** R$ 2.548.998,00  

### **✅ BATE? Sistema está CORRETO!**  
### **❌ NÃO BATE? Sistema tem erro!**

---

## 🧪 **VALIDAR AS 3 COLUNAS:**

Repita o processo para **TODAS as 3 colunas**:

### **Coluna C (Juros):**
```
Valor Base:      R$ 150.000,00
SELIC fev 0.99%: R$ 150.000,00 × 1.0099 = R$ 151.485,00
SELIC mar 0.96%: R$ 151.485,00 × 1.0096 = R$ 152.939,46
Esperado:        R$ 152.939,46
Sistema retornou: R$ 152.939,46  ← ✅ CORRETO!
```

### **Coluna D (Valor Atualizado):**
```
Valor Base:      R$ 2.500.000,00
SELIC fev 0.99%: R$ 2.500.000,00 × 1.0099 = R$ 2.524.750,00
SELIC mar 0.96%: R$ 2.524.750,00 × 1.0096 = R$ 2.548.998,00
Esperado:        R$ 2.548.998,00
Sistema retornou: R$ 2.548.998,00  ← ✅ CORRETO!
```

### **Coluna E (Honorários):**
```
Valor Base:      R$ 250.000,00
SELIC fev 0.99%: R$ 250.000,00 × 1.0099 = R$ 252.475,00
SELIC mar 0.96%: R$ 252.475,00 × 1.0096 = R$ 254.899,80
Esperado:        R$ 254.899,80
Sistema retornou: R$ 254.899,80  ← ✅ CORRETO!
```

---

## 📱 **VALIDAÇÃO COM CALCULADORA:**

Você pode usar qualquer calculadora (celular, computador, Excel):

### **Exemplo no Excel:**

```excel
A1: 2500000           (Valor Base)
A2: =A1 * 1.0099      (Após fev/2025)
A3: =A2 * 1.0096      (Após mar/2025)
```

Resultado em **A3** deve bater com o sistema!

---

## 🔍 **CASOS ESPECIAIS:**

### **Se a data de correção for 15/03/2025:**
- Aplica SELIC de **fevereiro inteiro** (2025-02)
- Aplica SELIC de **março inteiro** (2025-03)
- ⚠️ **Não importa o dia**: SELIC é mensal!

### **Se a data de correção for 01/02/2025:**
- Aplica **somente fevereiro** (2025-02)
- Não aplica janeiro (pois base já é 01/01/2025)

### **Se a data de correção for 01/01/2025:**
- **Não aplica nenhuma SELIC**
- Sistema retorna apenas "Resultados Base"

---

## 📊 **FÓRMULA COMPLETA (PARA PROGRAMADORES):**

```python
def calcular_selic_manual(valor_base, data_correcao):
    """
    Aplica SELIC composta de 01/01/2025 até data_correcao
    """
    from datetime import datetime
    
    # Carregar cache SELIC
    import json
    with open('../data/selic_cache.json', 'r') as f:
        selic_cache = json.load(f)
    
    # Gerar lista de meses
    data_base = datetime(2025, 1, 1)
    ano, mes = 2025, 1
    meses = []
    
    while True:
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1
        
        if ano > data_correcao.year or (ano == data_correcao.year and mes > data_correcao.month):
            break
        
        meses.append(f"{ano:04d}-{mes:02d}")
    
    # Aplicar SELIC composta
    valor = valor_base
    for mes in meses:
        taxa = selic_cache[mes]
        valor *= (1 + taxa / 100)
    
    return valor

# Exemplo de uso:
valor_final = calcular_selic_manual(2500000.00, datetime(2025, 3, 1))
print(f"R$ {valor_final:,.2f}")
```

---

## ✅ **CHECKLIST DE VALIDAÇÃO:**

- [ ] 1. Fiz um cálculo no sistema com data > 01/01/2025
- [ ] 2. Anotei os valores da seção "Resultados Base"
- [ ] 3. Anotei os valores da seção "Resultados Atualizados"
- [ ] 4. Busquei as taxas SELIC no `selic_cache.json`
- [ ] 5. Calculei manualmente: Base × (1 + SELIC1/100) × (1 + SELIC2/100) × ...
- [ ] 6. Comparei com os valores do sistema
- [ ] 7. Validei as 3 colunas (C, D, E)
- [ ] 8. Resultado: ✅ SISTEMA CORRETO / ❌ SISTEMA COM ERRO

---

## 🎯 **EXEMPLO COMPLETO:**

### **Cenário:**
- Município: TERESINA
- Data correção: **01/04/2025**
- Valor Base (Coluna D): R$ **1.000.000,00**

### **Taxas SELIC:**
```json
"2025-02": 0.99,
"2025-03": 0.96,
"2025-04": 0.95
```

### **Cálculo Manual:**
```
Passo 1: 1.000.000,00 × 1.0099 = 1.009.900,00
Passo 2: 1.009.900,00 × 1.0096 = 1.019.594,04
Passo 3: 1.019.594,04 × 1.0095 = 1.029.280,78
```

### **Resultado Esperado:** R$ **1.029.280,78**

### **Comparar com o sistema:**
Se o sistema retornou **R$ 1.029.280,78** → ✅ **CORRETO!**

---

## 💡 **DICAS:**

1. **Use uma calculadora com alta precisão** (não arredonde até o final)
2. **Valide com valores grandes** (R$ 1.000.000+) para ver diferenças
3. **Teste múltiplos meses** (fev, mar, abr, mai...)
4. **Compare todas as 3 colunas** (C, D, E)

---

## 🚨 **SE DER ERRO:**

### **Diferença pequena (< R$ 0,10):**
- ✅ **Normal!** Arredondamentos de ponto flutuante
- Sistema está **CORRETO**

### **Diferença grande (> R$ 1,00):**
- ❌ **Problema!** Pode ser:
  - SELIC sendo aplicada errada
  - Fórmula incorreta
  - Cache desatualizado

---

## 📞 **RESUMO EXECUTIVO:**

```
PEGUE:   Valor Base (Coluna D da seção "Resultados Base")
PEGUE:   Taxas SELIC dos meses (no selic_cache.json)
CALCULE: Valor × (1 + SELIC1/100) × (1 + SELIC2/100) × ...
COMPARE: Com Valor da seção "Resultados Atualizados"
RESULTADO: Se bater → Sistema CORRETO ✅
```

---

**Pronto para validar! 🚀**
