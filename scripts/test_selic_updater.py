"""
Teste simples da funcionalidade de atualização SELIC.

Executa teste unitário do SelicUpdater para validar a lógica de atualização.
"""

import sys
from pathlib import Path

# Adicionar backend ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from services.selic_updater import SelicUpdater
from datetime import datetime


def test_selic_updater():
    """
    Testa a funcionalidade de atualização SELIC.
    """
    print("🧪 Testando SelicUpdater...\n")
    
    # Inicializar updater
    updater = SelicUpdater("./data/selic_cache.json")
    
    # Teste 1: Data que NÃO precisa atualização
    print("📝 Teste 1: Data ≤ 01/01/2025")
    precisa = updater.precisa_atualizacao("01/01/2025")
    print(f"   Resultado: {precisa}")
    assert precisa == False, "Erro: Não deveria precisar de atualização"
    print("   ✅ Passou!\n")
    
    # Teste 2: Data que PRECISA atualização
    print("📝 Teste 2: Data > 01/01/2025")
    precisa = updater.precisa_atualizacao("01/03/2025")
    print(f"   Resultado: {precisa}")
    assert precisa == True, "Erro: Deveria precisar de atualização"
    print("   ✅ Passou!\n")
    
    # Teste 3: Cálculo de meses entre datas
    print("📝 Teste 3: Cálculo de meses entre datas")
    meses = updater._get_meses_entre_datas(
        datetime(2025, 1, 1),
        datetime(2025, 3, 15)
    )
    print(f"   Resultado: {meses}")
    assert meses == ['2025-02', '2025-03'], f"Erro: Esperado ['2025-02', '2025-03'], obteve {meses}"
    print("   ✅ Passou!\n")
    
    # Teste 4: Aplicação de SELIC composta
    print("📝 Teste 4: Aplicação de SELIC composta")
    valor_base = 1000.0
    meses_teste = ['2025-02', '2025-03']  # SELIC: 0.99% e 0.96%
    
    valor_atualizado = updater._aplicar_selic_composta(valor_base, meses_teste)
    
    # Cálculo esperado:
    # 1000 * (1 + 0.99/100) * (1 + 0.96/100)
    # 1000 * 1.0099 * 1.0096
    # ≈ 1019.49
    
    print(f"   Valor base: R$ {valor_base:.2f}")
    print(f"   SELIC 02/2025: 0.99%")
    print(f"   SELIC 03/2025: 0.96%")
    print(f"   Valor atualizado: R$ {valor_atualizado:.2f}")
    print(f"   Valorização: {((valor_atualizado - valor_base) / valor_base * 100):.2f}%")
    
    esperado = 1000 * 1.0099 * 1.0096
    assert abs(valor_atualizado - esperado) < 0.01, f"Erro: Esperado {esperado:.2f}, obteve {valor_atualizado:.2f}"
    print("   ✅ Passou!\n")
    
    # Teste 5: Atualização de resultados reais
    print("📝 Teste 5: Atualização de resultados completos")
    
    # Simular resultado da planilha
    results_mock = [
        {
            "titulo": "NT7 SELIC (SELIC desde quando devido até hoje)",
            "header": ["Descrição", "Valor Corrigido Mensal", "Valor dos Juros Mensal", "Valor Atualizado", "Honorários"],
            "rows": [
                ["Principal", 1000.0, 50.0, 1050.0, 105.0],
                ["Acessórios", 500.0, 25.0, 525.0, 52.5]
            ],
            "total": ["TOTAL", 1500.0, 75.0, 1575.0, 157.5]
        }
    ]
    
    results_atualizados = updater.atualizar_resultados(results_mock, "01/03/2025")
    
    print(f"   Tabelas atualizadas: {len(results_atualizados)}")
    print(f"   Título atualizado: {results_atualizados[0]['titulo']}")
    
    # Verificar se valores foram atualizados
    row_original = results_mock[0]["rows"][0]
    row_atualizada = results_atualizados[0]["rows"][0]
    
    print(f"\n   Linha 1 (Principal):")
    print(f"      Juros (C) - Original: R$ {row_original[2]:.2f}")
    print(f"      Juros (C) - Atualizado: R$ {row_atualizada[2]:.2f}")
    print(f"      Atualizado (D) - Original: R$ {row_original[3]:.2f}")
    print(f"      Atualizado (D) - Atualizado: R$ {row_atualizada[3]:.2f}")
    
    assert row_atualizada[2] > row_original[2], "Erro: Juros deveria ter aumentado"
    assert row_atualizada[3] > row_original[3], "Erro: Valor atualizado deveria ter aumentado"
    
    print("   ✅ Passou!\n")
    
    print("🎉 Todos os testes passaram com sucesso!")


if __name__ == "__main__":
    test_selic_updater()
