# Taxas SELIC mensais de 2025
TAXAS_SELIC = [
    0.99,  # fev/2025
    0.96,  # mar/2025
    1.06,  # abr/2025
    1.14,  # mai/2025
    1.10,  # jun/2025
    1.28,  # jul/2025
    1.16,  # ago/2025
    1.22,  # set/2025
    1.28   # out/2025
]

MESES = ["fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out"]

def formatar_moeda(valor):
    """Formata valor como moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def calcular_selic_acumulada():
    """Calcula SELIC acumulada mês a mês"""
    print("=" * 80)
    print("CALCULADORA DE SELIC COMPOSTA - 2025")
    print("=" * 80)
    
    while True:
        try:
            entrada = input("\nDigite o valor base: R$ ")
            entrada_limpa = entrada.replace('.', '').replace(',', '.')
            valor_base = float(entrada_limpa)
            break
        except ValueError:
            print("Valor inválido! Digite um número (ex: 1000000 ou 1.000.000,00)")
    
    print(f"\n{'='*80}")
    print(f"VALOR BASE: {formatar_moeda(valor_base)}")
    print(f"{'='*80}\n")
    
    valor_atual = valor_base
    fator_acumulado = 1.0
    
    for i, (mes, taxa) in enumerate(zip(MESES, TAXAS_SELIC), start=2):
        fator_mensal = 1 + (taxa / 100)
        fator_acumulado *= fator_mensal
        valor_atual = valor_base * fator_acumulado
        
        print(f"mês {i:2d} — {mes}/2025: × {fator_acumulado:.20f}")
        print(f"         SELIC: {taxa:5.2f}%  →  {formatar_moeda(valor_atual)}")
        print()
    


if __name__ == "__main__":
    calcular_selic_acumulada()
    
    while True:
        resposta = input("\nDeseja calcular outro valor? (s/n): ").lower()
        if resposta == 's':
            print("\n")
            calcular_selic_acumulada()
        elif resposta == 'n':
            print("\nEncerrando...")
            break
        else:
            print("Digite 's' para sim ou 'n' para não")
