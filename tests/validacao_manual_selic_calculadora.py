import json
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURAÇÃO: Preencha com os valores do seu teste
# ============================================================================

# 1. VALOR BASE (da seção "Resultados Base (01/01/2025)")
#    Pegue o valor da linha TOTAL, coluna D (Valor Atualizado)
VALOR_BASE = 373_207_843.41  # ← COLOQUE AQUI o valor que você viu

# 2. DATA DE CORREÇÃO
#    Data que você colocou no formulário
DATA_CORRECAO = "01/09/2025"  # ← COLOQUE AQUI (formato DD/MM/YYYY)

# 3. VALOR QUE O SISTEMA RETORNOU (da seção "Resultados Atualizados")
#    Pegue o valor da linha TOTAL, coluna D (Valor Atualizado)
VALOR_SISTEMA = 407_784_507.04  # ← COLOQUE AQUI o valor do sistema

# ============================================================================
# CÓDIGO (NÃO MEXER ABAIXO)
# ============================================================================

def carregar_selic_cache():
    """Carrega o cache de SELIC"""
    cache_path = Path(__file__).parent.parent / "data" / "selic_cache.json"
    with open(cache_path, 'r') as f:
        return json.load(f)

def parse_data(data_str):
    """Converte DD/MM/YYYY para datetime"""
    dia, mes, ano = data_str.split('/')
    return datetime(int(ano), int(mes), int(dia))

def gerar_meses(data_fim):
    """Gera lista de meses entre 01/01/2025 e data_fim"""
    meses = []
    ano, mes = 2025, 1
    
    data_correcao = parse_data(data_fim)
    
    while True:
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1
        
        if ano > data_correcao.year or (ano == data_correcao.year and mes > data_correcao.month):
            break
        
        meses.append(f"{ano:04d}-{mes:02d}")
    
    return meses

def formatar_moeda(valor):
    """Formata valor como moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def main():
    print("=" * 80)
    print("CALCULADORA DE VALIDAÇÃO MANUAL DE SELIC")
    print("=" * 80)
    
    # Carregar cache
    print("\n Carregando taxas SELIC...")
    selic_cache = carregar_selic_cache()
    print(f"✅ {len(selic_cache)} meses de SELIC carregados")
    
    # Gerar meses
    print(f"\n Gerando meses entre 01/01/2025 e {DATA_CORRECAO}...")
    meses = gerar_meses(DATA_CORRECAO)
    
    if not meses:
        print(" Nenhum mês de SELIC a aplicar (data ≤ 01/01/2025)")
        print(f"\nValor Base:   {formatar_moeda(VALOR_BASE)}")
        print(f"Valor Final:  {formatar_moeda(VALOR_BASE)}")
        return
    
    print(f" {len(meses)} meses encontrados: {', '.join(meses)}")
    
    # Calcular passo a passo
    print("\n" + "=" * 80)
    print("CÁLCULO PASSO A PASSO")
    print("=" * 80)
    
    print(f"\n Valor Base (01/01/2025): {formatar_moeda(VALOR_BASE)}")
    print("\n Aplicando SELIC mês a mês:")
    
    valor_atual = VALOR_BASE
    
    for i, mes in enumerate(meses, 1):
        taxa = selic_cache.get(mes)
        
        if taxa is None:
            print(f"\n ERRO: SELIC não encontrada para {mes}!")
            print(f"   Verifique o arquivo data/selic_cache.json")
            return
        
        # Calcular
        valor_anterior = valor_atual
        fator = 1 + (taxa / 100)
        valor_atual = valor_atual * fator
        
        # Mostrar cálculo
        print(f"\n   Passo {i} - {mes}: {taxa}%")
        print(f"   {formatar_moeda(valor_anterior)} × {fator:.6f} = {formatar_moeda(valor_atual)}")
    
    # Resultado final
    print("\n" + "=" * 80)
    print("RESULTADO")
    print("=" * 80)
    
    print(f"\n Valor Base (01/01/2025):           {formatar_moeda(VALOR_BASE)}")
    print(f" Valor Calculado Manualmente:       {formatar_moeda(valor_atual)}")
    print(f" Valor que o Sistema Retornou:      {formatar_moeda(VALOR_SISTEMA)}")
    
    # Comparação
    diferenca = abs(valor_atual - VALOR_SISTEMA)
    diferenca_pct = (diferenca / VALOR_SISTEMA * 100) if VALOR_SISTEMA > 0 else 0
    
    print(f"\n Diferença: {formatar_moeda(diferenca)} ({diferenca_pct:.4f}%)")
    
    # Veredito
    print("\n" + "=" * 80)
    if diferenca < 0.01:
        print(" TESTE PASSOU!")
        print(" Sistema está aplicando SELIC CORRETAMENTE!")
        print(" Diferença desprezível (arredondamento)")
    elif diferenca < 1.00:
        print(" TESTE PASSOU COM RESSALVAS")
        print(" Pequena diferença detectada (< R$ 1,00)")
        print(" Pode ser arredondamento de ponto flutuante")
        print(" Mas o cálculo está basicamente correto")
    else:
        print(" TESTE FALHOU!")
        print(" Sistema NÃO está aplicando SELIC corretamente!")
        print(" Diferença significativa detectada")
        print("\n Possíveis causas:")
        print("   - Fórmula de SELIC incorreta")
        print("   - Meses de SELIC calculados errados")
        print("   - Cache desatualizado")
        print("   - Valor base ou sistema incorreto")
    print("=" * 80)
    
    # Fórmula matemática
    print("\n Fórmula aplicada:")
    print(f"   Valor Final = {formatar_moeda(VALOR_BASE)}", end="")
    for mes in meses:
        taxa = selic_cache[mes]
        print(f" × (1 + {taxa}/100)", end="")
    print()
    
    print("\n Para validar outras colunas:")
    print("   1. Copie o valor base da Coluna C (Juros)")
    print("   2. Modifique VALOR_BASE no topo deste arquivo")
    print("   3. Copie o valor do sistema da Coluna C atualizada")
    print("   4. Modifique VALOR_SISTEMA")
    print("   5. Execute novamente: python validacao_manual_selic_calculadora.py")
    print("\n   Repita para Coluna E (Honorários)")

if __name__ == "__main__":
    main()
