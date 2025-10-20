"""
Script para identificar quais células/tabelas usam SELIC no cálculo.

Este script analisa a planilha Excel e identifica:
1. Células que contêm a palavra "SELIC" no nome/fórmula
2. Colunas que dependem de correção monetária
3. Quais das 17 tabelas precisam ser atualizadas

Executar: python scripts/identify_selic_cells.py
"""

import xlwings as xw
from pathlib import Path
import json


def analyze_selic_dependencies(excel_path: str):
    """
    Analisa a planilha para identificar dependências da SELIC.
    """
    print(f"📊 Analisando planilha: {excel_path}")
    
    # Abrir Excel em modo invisível
    app = xw.App(visible=False)
    wb = app.books.open(excel_path)
    sheet = wb.sheets["RESUMO"]
    
    results = {
        "selic_cells": [],
        "correcao_monetaria_columns": [],
        "tabelas_afetadas": []
    }
    
    # 1. Procurar por células que mencionam "SELIC"
    print("\n🔍 Procurando células com 'SELIC'...")
    for row in range(1, 105):  # Linhas 1-104
        for col_letter in ['A', 'B', 'C', 'D', 'E', 'F', 'AB']:
            cell = sheet.range(f'{col_letter}{row}')
            value = cell.value
            
            # Verificar valor
            if value and isinstance(value, str) and 'SELIC' in value.upper():
                print(f"   ✓ Encontrado em {col_letter}{row}: {value}")
                results["selic_cells"].append({
                    "cell": f"{col_letter}{row}",
                    "value": value
                })
            
            # Verificar fórmula
            try:
                formula = cell.formula
                if formula and 'SELIC' in formula.upper():
                    print(f"   ✓ Fórmula SELIC em {col_letter}{row}")
                    results["selic_cells"].append({
                        "cell": f"{col_letter}{row}",
                        "formula": formula
                    })
            except:
                pass
    
    # 2. Identificar colunas de correção monetária (geralmente coluna D ou E)
    print("\n🔍 Analisando cabeçalhos das tabelas (linhas 21-104)...")
    linha_atual = 21
    while linha_atual <= 104:
        # Verificar se é uma linha de cabeçalho
        primeira_celula = sheet.range(f'A{linha_atual}').value
        
        if primeira_celula and "Descrição" in str(primeira_celula):
            # É um cabeçalho de tabela
            titulo_linha = linha_atual - 1
            titulo = sheet.range(f'A{titulo_linha}').value
            
            print(f"\n   📋 Tabela: {titulo}")
            
            # Ler cabeçalho
            header = []
            for col in ['A', 'B', 'C', 'D', 'E', 'F', 'AB']:
                val = sheet.range(f'{col}{linha_atual}').value
                header.append(str(val) if val else "")
            
            print(f"      Cabeçalho: {header}")
            
            # Identificar colunas relacionadas a correção/juros/SELIC
            keywords = ['CORREÇÃO', 'JUROS', 'SELIC', 'MONETÁRIA', 'ATUALIZADO']
            afetadas = []
            
            for idx, h in enumerate(header):
                if h and any(keyword in h.upper() for keyword in keywords):
                    col_letter = ['A', 'B', 'C', 'D', 'E', 'F', 'AB'][idx]
                    afetadas.append(col_letter)
                    print(f"      ✓ Coluna {col_letter}: {h}")
            
            if afetadas:
                results["tabelas_afetadas"].append({
                    "titulo": titulo,
                    "linha_inicio": titulo_linha,
                    "colunas_selic": afetadas,
                    "header": header
                })
            
            linha_atual += 5  # Pular para próxima tabela
        else:
            linha_atual += 1
    
    # Fechar Excel
    wb.close()
    app.quit()
    
    # 3. Salvar resultados
    output_path = Path(__file__).parent.parent / "data" / "selic_mapping.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Análise completa! Resultados salvos em: {output_path}")
    print(f"\n📊 Resumo:")
    print(f"   - Células com SELIC: {len(results['selic_cells'])}")
    print(f"   - Tabelas afetadas: {len(results['tabelas_afetadas'])}")
    
    return results


if __name__ == "__main__":
    # Caminho da planilha
    base_dir = Path(__file__).parent.parent
    excel_path = base_dir / "data" / "planilhamae.xlsx"
    
    if not excel_path.exists():
        print(f"❌ Planilha não encontrada: {excel_path}")
        print("   Por favor, coloque a planilha em data/planilhamae.xlsx")
    else:
        analyze_selic_dependencies(str(excel_path))
