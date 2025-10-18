"""
Serviço de integração com Excel via xlwings.
Responsável por escrever dados na planilha, executar cálculos e ler resultados.

DECISÕES TÉCNICAS:
- xlwings para manter fórmulas ativas no Excel
- Leitura linha a linha para identificar blocos (título, cabeçalho, valores, total)
- Tratamento especial para "TOTAL DO VALOR PROPOSTO PARA ACORDO" (apenas colunas A-C)
"""

import xlwings as xw
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from decimal import Decimal
import re


class ExcelRunner:
    def __init__(self, excel_path: str, mapa_celulas_path: str):
        self.excel_path = Path(excel_path)
        self.mapa_celulas_path = Path(mapa_celulas_path)
        
        # Carregar o mapa de células
        with open(self.mapa_celulas_path, 'r', encoding='utf-8') as f:
            self.mapa = json.load(f)
        
        self.app = None
        self.wb = None
        self.sheet = None
    
    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """
        Converte string de data DD/MM/YYYY para objeto datetime.
        Excel precisa de datetime para interpretar corretamente.
        """
        if not date_str or not isinstance(date_str, str):
            return date_str
        
        # Tentar formatos comuns
        for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        # Se não conseguir parsear, retornar original
        return date_str
    
    def _read_cell_value(self, cell_address: str) -> Any:
        """
        Lê o valor de uma célula considerando seu formato.
        Se a célula estiver formatada como percentual (%), divide por 100.
        """
        cell = self.sheet.range(cell_address)
        value = cell.value
        
        # Verificar se a célula está formatada como percentual
        cell_format = cell.number_format
        if cell_format and '%' in cell_format and isinstance(value, (int, float)) and value != 0:
            # Célula formatada como % - o valor já está multiplicado por 100
            # Precisamos dividir para obter o valor real
            return value / 100
        
        return value
    
    @staticmethod
    def _convert_value(value: Any) -> Any:
        """
        Converte valores do Excel para tipos serializáveis em JSON.
        
        - Decimal → float
        - datetime → string ISO
        - None → None
        - Outros → mantém
        """
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        
        if isinstance(value, Decimal):
            return float(value)
        
        if isinstance(value, datetime):
            return value.isoformat()
        
        # Se for string vazia, retornar None
        if isinstance(value, str) and not value.strip():
            return None
        
        return value
    
    def __enter__(self):
        """Abre o Excel ao entrar no contexto."""
        self.app = xw.App(visible=False)
        self.wb = self.app.books.open(str(self.excel_path.absolute()))
        self.sheet = self.wb.sheets[self.mapa['aba']]
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha o Excel ao sair do contexto."""
        if self.wb:
            self.wb.close()
        if self.app:
            self.app.quit()
    
    def write_inputs(self, data: Dict[str, Any]) -> None:
        """
        Escreve os dados de entrada nas células correspondentes da aba RESUMO.
        
        Mapeamento (conforme prompt):
        - município → B6
        - ajuizamento → B7
        - citação → B8
        - início_cálculo → B9
        - final_cálculo → B10
        - honorários_s_valor_da_condenação → B11
        - honorários_em_valor_fixo → B12
        - deságio_a_aplicar_sobre_o_principal → B13
        - deságio_em_a_aplicar_em_honorários → B14
        - correção_até → B15
        """
        # Mapeamento conforme o prompt (B6 a B15)
        campo_para_celula = {
            "município": "B6",
            "ajuizamento": "B7",
            "citação": "B8",
            "início_cálculo": "B9",
            "final_cálculo": "B10",
            "honorários_s_valor_da_condenação": "B11",
            "honorários_em_valor_fixo": "B12",
            "deságio_a_aplicar_sobre_o_principal": "B13",
            "deságio_em_a_aplicar_em_honorários": "B14",
            "correção_até": "B15"
        }
        
        # Campos que são datas e precisam ser convertidos
        campos_data = [
            "ajuizamento", "citação", "início_cálculo", 
            "final_cálculo", "correção_até"
        ]
        
        # Campos que são percentuais (células formatadas como %) - dividir por 100
        campos_percentual = [
            "honorários_s_valor_da_condenação",  # B11
            "deságio_a_aplicar_sobre_o_principal",  # B13
            "deságio_em_a_aplicar_em_honorários"  # B14
        ]
        
        for campo, valor in data.items():
            celula = campo_para_celula.get(campo)
            if celula:
                # Converter datas para datetime
                if campo in campos_data and isinstance(valor, str):
                    valor = self._parse_date(valor)
                
                # Converter percentuais: 20 → 0.20 (para células formatadas como %)
                if campo in campos_percentual and isinstance(valor, (int, float)):
                    valor = valor / 100
                
                # Escrever na célula
                self.sheet.range(celula).value = valor
        
        # ADICIONAL: Escrever também nas células amarelas do Período (E6 e F6)
        # Estas células são as que a planilha realmente usa para cálculo
        if "início_cálculo" in data:
            valor_inicio = data["início_cálculo"]
            if isinstance(valor_inicio, str):
                valor_inicio = self._parse_date(valor_inicio)
            self.sheet.range("E6").value = valor_inicio
            
        if "final_cálculo" in data:
            valor_fim = data["final_cálculo"]
            if isinstance(valor_fim, str):
                valor_fim = self._parse_date(valor_fim)
            self.sheet.range("F6").value = valor_fim
    
    def calculate(self) -> None:
        """Executa o recálculo da planilha."""
        self.wb.app.calculate()
    
    def read_results(self) -> List[Dict[str, Any]]:
        """
        Lê as tabelas vermelhas (linhas 21-104, colunas A-F e AB).
        
        ESTRUTURA DE CADA BLOCO:
        - Linha N: Título (coluna A)
        - Linha N+1: Cabeçalho (colunas A-F + AB)
        - Linha N+2: Valores (colunas A-F + AB)
        - Linha N+3: Total (colunas A-F + AB)
        - Linha N+4: Vazia (espaçamento)
        
        NOTA: Todos os blocos, incluindo "TOTAL DO VALOR PROPOSTO PARA ACORDO",
        usam todas as colunas (A-F + AB).
        """
        results = []
        linha_atual = self.mapa['tabelas']['inicio']  # 21
        linha_fim = self.mapa['tabelas']['fim']  # 104
        
        # Colunas conforme prompt: A-F e AB
        colunas_principais = ['A', 'B', 'C', 'D', 'E', 'F']
        coluna_ab = 'AB'
        
        while linha_atual <= linha_fim:
            # Ler possível título na coluna A
            titulo_cell = self.sheet.range(f'A{linha_atual}').value
            
            if not titulo_cell or str(titulo_cell).strip() == "":
                linha_atual += 1
                continue
            
            titulo = str(titulo_cell).strip()
            
            # Verificar se a próxima linha é um cabeçalho
            proxima_linha = linha_atual + 1
            if proxima_linha > linha_fim:
                break
            
            primeira_celula_proxima = self.sheet.range(f'A{proxima_linha}').value
            
            # Se a próxima linha contém "Descrição", é um cabeçalho de tabela
            if primeira_celula_proxima and "Descrição" in str(primeira_celula_proxima):
                # Ler cabeçalho (A-F)
                header = []
                for col in colunas_principais:
                    val = self.sheet.range(f'{col}{proxima_linha}').value
                    header.append(str(val) if val else "")
                
                # Adicionar coluna AB ao cabeçalho
                val_ab = self.sheet.range(f'{coluna_ab}{proxima_linha}').value
                header.append(str(val_ab) if val_ab else "")
                
                # Ler valores (próximas linhas até encontrar linha vazia ou "TOTAL")
                rows = []
                linha_valores = proxima_linha + 1
                
                while linha_valores <= linha_fim:
                    primeira_col = self.sheet.range(f'A{linha_valores}').value
                    
                    # Parar se linha vazia
                    if not primeira_col or str(primeira_col).strip() == "":
                        break
                    
                    # Parar se encontrar "TOTAL"
                    if "TOTAL" in str(primeira_col).upper():
                        break
                    
                    # Ler valores (A-F + AB)
                    row_data = []
                    for col in colunas_principais:
                        val = self._read_cell_value(f'{col}{linha_valores}')
                        row_data.append(self._convert_value(val))
                    
                    # Adicionar valor da coluna AB
                    val_ab = self._read_cell_value(f'{coluna_ab}{linha_valores}')
                    row_data.append(self._convert_value(val_ab))
                    
                    rows.append(row_data)
                    linha_valores += 1
                
                # Ler linha de TOTAL (se existir)
                total = None
                if linha_valores <= linha_fim:
                    primeira_col_total = self.sheet.range(f'A{linha_valores}').value
                    if primeira_col_total and "TOTAL" in str(primeira_col_total).upper():
                        # Ler todas as colunas A-F + AB para qualquer tipo de TOTAL
                        total = []
                        for col in colunas_principais:
                            val = self._read_cell_value(f'{col}{linha_valores}')
                            total.append(self._convert_value(val))
                        
                        val_ab = self._read_cell_value(f'{coluna_ab}{linha_valores}')
                        total.append(self._convert_value(val_ab))
                
                # Adicionar resultado
                bloco = {
                    "titulo": titulo,
                    "header": header,
                    "rows": rows
                }
                
                if total:
                    bloco["total"] = total
                
                results.append(bloco)
                
                # Avançar para próximo bloco (pular linha de total + espaçamento)
                linha_atual = linha_valores + 2
            else:
                # Não é uma tabela, apenas avançar
                linha_atual += 1
        
        return results
