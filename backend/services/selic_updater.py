"""
Serviço de atualização de valores com SELIC.

Aplica correção SELIC mensal progressiva sobre os valores base (01/01/2025)
para datas posteriores escolhidas pelo usuário.

DECISÕES TÉCNICAS:
- Base: Valores da planilha em 01/01/2025
- Método: Aplicação de SELIC mensal composta (1 + selic_mensal)
- Colunas atualizadas: C (Juros), D (Valor Atualizado), E (Honorários)
"""

from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import json
from .selic_api import SelicAPI


class SelicUpdater:
    """
    Atualiza resultados da planilha aplicando SELIC mensal progressiva.
    """
    
    # Data base dos resultados da planilha
    DATA_BASE = datetime(2025, 1, 1)
    
    # Índices das colunas que precisam ser atualizadas
    COLUNA_JUROS = 2  # Coluna C (índice 2)
    COLUNA_ATUALIZADO = 3  # Coluna D (índice 3)
    COLUNA_HONORARIOS = 4  # Coluna E (índice 4)
    
    def __init__(self, selic_cache_path: str = "./data/selic_cache.json"):
        self.selic_api = SelicAPI(selic_cache_path)
        
        # Carregar mapeamento de tabelas que usam SELIC
        mapping_path = Path(selic_cache_path).parent / "selic_mapping.json"
        if mapping_path.exists():
            with open(mapping_path, 'r', encoding='utf-8') as f:
                self.mapping = json.load(f)
        else:
            self.mapping = {"tabelas_afetadas": []}
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        Converte string de data DD/MM/YYYY para objeto datetime.
        """
        if isinstance(date_str, datetime):
            return date_str
        
        for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Data inválida: {date_str}")
    
    def _get_meses_entre_datas(self, data_inicio: datetime, data_fim: datetime) -> List[str]:
        """
        Retorna lista de meses entre duas datas no formato YYYY-MM.
        Exemplo: data_inicio=2025-01-01, data_fim=2025-03-15
                 Retorna: ['2025-02', '2025-03']
        """
        meses = []
        
        # Começar do mês seguinte à data base
        ano = data_inicio.year
        mes = data_inicio.month
        
        while True:
            # Avançar para o próximo mês
            mes += 1
            if mes > 12:
                mes = 1
                ano += 1
            
            # Verificar se passou da data fim
            if ano > data_fim.year or (ano == data_fim.year and mes > data_fim.month):
                break
            
            meses.append(f"{ano:04d}-{mes:02d}")
        
        return meses
    
    def _aplicar_selic_composta(self, valor_base: float, meses: List[str]) -> float:
        """
        Aplica SELIC composta mensal sobre um valor base.
        
        Fórmula: valor_final = valor_base * (1 + selic_mes1/100) * (1 + selic_mes2/100) * ...
        
        Args:
            valor_base: Valor inicial em 01/01/2025
            meses: Lista de meses no formato YYYY-MM
        
        Returns:
            Valor atualizado após aplicação da SELIC
        """
        if valor_base is None or valor_base == 0:
            return valor_base
        
        valor_atual = valor_base
        
        for mes in meses:
            selic_mensal = self.selic_api.get_selic_for_month(mes)
            
            if selic_mensal is None:
                # Se não tiver SELIC para o mês, tentar buscar da API
                try:
                    selic_mensal = self.selic_api.ensure_selic(f"01/{mes.split('-')[1]}/{mes.split('-')[0]}")
                except:
                    # Se não conseguir, usar 0 (sem correção)
                    selic_mensal = 0
            
            # Aplicar SELIC: valor_atual * (1 + selic/100)
            if selic_mensal and selic_mensal != 0:
                fator = 1 + (selic_mensal / 100)
                valor_atual = valor_atual * fator
        
        return valor_atual
    
    def precisa_atualizacao(self, correcao_ate: str) -> bool:
        """
        Verifica se a data de correção é posterior à data base (01/01/2025).
        """
        try:
            data_correcao = self._parse_date(correcao_ate)
            return data_correcao > self.DATA_BASE
        except:
            return False
    
    def atualizar_resultados(self, results: List[Dict[str, Any]], correcao_ate: str) -> List[Dict[str, Any]]:
        """
        Atualiza os resultados aplicando SELIC mensal desde 01/01/2025 até a data especificada.
        
        Args:
            results: Lista de tabelas com resultados base (01/01/2025)
            correcao_ate: Data de correção no formato DD/MM/YYYY
        
        Returns:
            Nova lista de tabelas com valores atualizados
        """
        # Verificar se precisa atualizar
        if not self.precisa_atualizacao(correcao_ate):
            return results
        
        # Calcular meses de SELIC a aplicar
        data_correcao = self._parse_date(correcao_ate)
        meses_selic = self._get_meses_entre_datas(self.DATA_BASE, data_correcao)
        
        if not meses_selic:
            return results
        
        print(f"Aplicando SELIC de {meses_selic[0]} a {meses_selic[-1]} ({len(meses_selic)} meses)")
        
        # Criar cópia profunda dos resultados
        results_atualizados = []
        
        for table in results:
            table_copy = {
                "titulo": f"{table['titulo']} - ATUALIZADO ATÉ {correcao_ate}",
                "header": table["header"].copy(),
                "rows": []
            }
            
            # Atualizar cada linha
            for row in table["rows"]:
                row_copy = row.copy()
                
                # Atualizar Coluna C (Juros)
                if len(row_copy) > self.COLUNA_JUROS and isinstance(row_copy[self.COLUNA_JUROS], (int, float)):
                    valor_base = row_copy[self.COLUNA_JUROS]
                    row_copy[self.COLUNA_JUROS] = self._aplicar_selic_composta(valor_base, meses_selic)
                
                # Atualizar Coluna D (Valor Atualizado)
                if len(row_copy) > self.COLUNA_ATUALIZADO and isinstance(row_copy[self.COLUNA_ATUALIZADO], (int, float)):
                    valor_base = row_copy[self.COLUNA_ATUALIZADO]
                    row_copy[self.COLUNA_ATUALIZADO] = self._aplicar_selic_composta(valor_base, meses_selic)
                
                # Atualizar Coluna E (Honorários)
                if len(row_copy) > self.COLUNA_HONORARIOS and isinstance(row_copy[self.COLUNA_HONORARIOS], (int, float)):
                    valor_base = row_copy[self.COLUNA_HONORARIOS]
                    row_copy[self.COLUNA_HONORARIOS] = self._aplicar_selic_composta(valor_base, meses_selic)
                
                table_copy["rows"].append(row_copy)
            
            # Atualizar linha de total (se existir)
            if "total" in table and table["total"]:
                total_copy = table["total"].copy()
                
                # Atualizar Coluna C (Juros)
                if len(total_copy) > self.COLUNA_JUROS and isinstance(total_copy[self.COLUNA_JUROS], (int, float)):
                    valor_base = total_copy[self.COLUNA_JUROS]
                    total_copy[self.COLUNA_JUROS] = self._aplicar_selic_composta(valor_base, meses_selic)
                
                # Atualizar Coluna D (Valor Atualizado)
                if len(total_copy) > self.COLUNA_ATUALIZADO and isinstance(total_copy[self.COLUNA_ATUALIZADO], (int, float)):
                    valor_base = total_copy[self.COLUNA_ATUALIZADO]
                    total_copy[self.COLUNA_ATUALIZADO] = self._aplicar_selic_composta(valor_base, meses_selic)
                
                # Atualizar Coluna E (Honorários)
                if len(total_copy) > self.COLUNA_HONORARIOS and isinstance(total_copy[self.COLUNA_HONORARIOS], (int, float)):
                    valor_base = total_copy[self.COLUNA_HONORARIOS]
                    total_copy[self.COLUNA_HONORARIOS] = self._aplicar_selic_composta(valor_base, meses_selic)
                
                table_copy["total"] = total_copy
            
            results_atualizados.append(table_copy)
        
        return results_atualizados
