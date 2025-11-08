"""
Debug: Verificar cálculo SELIC exato
"""

# Valor base
valor_base = 1204809414.31

# Taxas SELIC de fev a out/2025
taxas = [0.99, 0.96, 1.06, 1.14, 1.10, 1.28, 1.16, 1.22, 0.72]

print("=" * 80)
print("CÁLCULO PASSO A PASSO")
print("=" * 80)
print(f"\nValor Base: R$ {valor_base:,.2f}")
print("\nAplicando SELIC mês a mês:\n")

valor_atual = valor_base
for i, taxa in enumerate(taxas, start=2):
    fator = 1 + (taxa / 100)
    valor_anterior = valor_atual
    valor_atual = valor_atual * fator
    print(f"Mês {i:2d} (SELIC {taxa:5.2f}%): R$ {valor_anterior:20,.2f} × {fator:.10f} = R$ {valor_atual:20,.2f}")

print("\n" + "=" * 80)
print("RESULTADO FINAL")
print("=" * 80)
print(f"\nValor Base:          R$ {valor_base:,.2f}")
print(f"Valor Calculado:     R$ {valor_atual:,.2f}")
print(f"Valor do Sistema:    R$ 1.325.909.947,07")
print(f"Diferença:           R$ {abs(valor_atual - 1325909947.07):,.2f}")
print(f"Diferença %:         {abs(valor_atual - 1325909947.07) / 1325909947.07 * 100:.6f}%")

# Calcular fator total
fator_total = valor_atual / valor_base
print(f"\nFator Total:         {fator_total:.20f}")
print(f"Fator Simplificado:  1.10078")
print(f"Diferença no fator:  {abs(fator_total - 1.10078):.20f}")
