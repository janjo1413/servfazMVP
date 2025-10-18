"""
Serviço de integração com a API do Banco Central (SELIC).
Garante que os dados SELIC estejam atualizados na planilha e em cache local.

DECISÕES TÉCNICAS:
- API oficial: https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json
- Cache local em JSON para evitar requisições repetidas
- Validação da data "correção_até" para determinar se precisa atualizar
"""

import httpx
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List


class SelicAPI:
    """
    Gerencia a obtenção e cache dos dados SELIC do Banco Central.
    """
    
    API_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json"
    
    def __init__(self, cache_path: str = "./data/selic_cache.json"):
        self.cache_path = Path(cache_path)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Carrega o cache local de dados SELIC."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_cache(self) -> None:
        """Salva o cache local de dados SELIC."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Converte uma data string para formato YYYY-MM.
        Aceita formatos: DD/MM/YYYY, YYYY-MM-DD, etc.
        """
        try:
            # Tentar vários formatos
            for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]:
                try:
                    dt = datetime.strptime(date_str.strip(), fmt)
                    return dt.strftime("%Y-%m")
                except ValueError:
                    continue
            return None
        except Exception:
            return None
    
    def fetch_selic_data(self) -> List[Dict]:
        """
        Busca todos os dados SELIC da API do Banco Central.
        Retorna lista de dicionários com formato: [{"data": "01/01/2020", "valor": "4.40"}, ...]
        """
        try:
            response = httpx.get(self.API_URL, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Erro ao buscar dados SELIC da API: {str(e)}")
    
    def ensure_selic(self, correcao_ate: str) -> Optional[float]:
        """
        Garante que o mês da "correção até" existe no cache/planilha.
        Se não existir, busca na API e atualiza o cache.
        
        Args:
            correcao_ate: Data de correção em formato string (ex: "15/01/2024")
        
        Returns:
            Valor SELIC do mês ou None se não encontrado
        """
        # Parsear a data para formato YYYY-MM
        mes_ano = self._parse_date(correcao_ate)
        
        if not mes_ano:
            raise ValueError(f"Data inválida para correção: {correcao_ate}")
        
        # Verificar se já existe no cache
        if mes_ano in self.cache:
            return self.cache[mes_ano]
        
        # Buscar dados atualizados da API
        print(f"📡 Buscando dados SELIC para {mes_ano} na API do Banco Central...")
        selic_data = self.fetch_selic_data()
        
        # Atualizar o cache com todos os dados
        for item in selic_data:
            data_item = item.get("data", "")
            valor_item = item.get("valor", "")
            
            # Converter data "01/MM/YYYY" para "YYYY-MM"
            try:
                dt = datetime.strptime(data_item, "%d/%m/%Y")
                chave = dt.strftime("%Y-%m")
                self.cache[chave] = float(valor_item)
            except Exception:
                continue
        
        # Salvar cache atualizado
        self._save_cache()
        
        # Retornar o valor solicitado
        return self.cache.get(mes_ano)
    
    def get_selic_for_month(self, mes_ano: str) -> Optional[float]:
        """
        Retorna o valor SELIC para um mês específico (formato: YYYY-MM).
        """
        return self.cache.get(mes_ano)
