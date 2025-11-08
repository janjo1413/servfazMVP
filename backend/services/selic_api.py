"""
Serviço de integração com a API do Banco Central (SELIC).
Garante que os dados SELIC estejam atualizados na planilha e em cache local.

DECISÕES TÉCNICAS:
- API oficial: https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json
- Cache local em JSON para evitar requisições repetidas
- APENAS MESES COMPLETOS: Usa mês atual - 1 para evitar dados incompletos
- Atualização automática: Valida idade do cache (24h)
"""

import httpx
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List


class SelicAPI:
    """
    Gerencia a obtenção e cache dos dados SELIC do Banco Central.
    Implementa validação de meses completos e atualização automática.
    """
    
    API_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.4390/dados?formato=json"
    CACHE_MAX_AGE_HOURS = 24  # Atualizar cache se mais antigo que 24h
    
    def __init__(self, cache_path: str = "./data/selic_cache.json"):
        self.cache_path = Path(cache_path)
        self.cache = self._load_cache()
        self.cache_metadata = self._load_metadata()
        
        # Atualizar automaticamente se cache estiver desatualizado
        if self._cache_needs_update():
            print("Cache SELIC desatualizado. Atualizando...")
            self.update_cache()
    
    def _load_cache(self) -> Dict:
        """Carrega o cache local de dados SELIC."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Se o cache tem metadata, retornar só os dados
                    if isinstance(data, dict) and '_metadata' in data:
                        return {k: v for k, v in data.items() if k != '_metadata'}
                    return data
            except Exception:
                return {}
        return {}
    
    def _load_metadata(self) -> Dict:
        """Carrega metadata do cache (última atualização, etc)."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and '_metadata' in data:
                        return data['_metadata']
            except Exception:
                pass
        return {"last_update": None}
    
    def _save_cache(self) -> None:
        """Salva o cache local de dados SELIC com metadata."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Atualizar metadata
        self.cache_metadata['last_update'] = datetime.now().isoformat()
        
        # Salvar cache + metadata
        cache_with_metadata = {**self.cache, '_metadata': self.cache_metadata}
        
        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_with_metadata, f, indent=2, ensure_ascii=False)
    
    def _cache_needs_update(self) -> bool:
        """Verifica se o cache precisa ser atualizado."""
        last_update = self.cache_metadata.get('last_update')
        
        if not last_update:
            return True  # Nunca foi atualizado
        
        try:
            last_update_dt = datetime.fromisoformat(last_update)
            age = datetime.now() - last_update_dt
            return age > timedelta(hours=self.CACHE_MAX_AGE_HOURS)
        except:
            return True  # Erro ao parsear, forçar atualização
    
    def _get_ultimo_mes_completo(self) -> str:
        """
        Retorna o último mês COMPLETO no formato YYYY-MM.
        Lógica: Mês atual - 1 (para garantir que está completo)
        
        Exemplo: Se hoje é 08/11/2025, retorna "2025-10" (outubro completo)
        """
        hoje = datetime.now()
        
        # Mês anterior
        if hoje.month == 1:
            ano = hoje.year - 1
            mes = 12
        else:
            ano = hoje.year
            mes = hoje.month - 1
        
        return f"{ano:04d}-{mes:02d}"
    
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
    
    def update_cache(self) -> None:
        """
        Atualiza o cache com dados da API, filtrando apenas meses completos.
        """
        print(f"Buscando dados SELIC da API do Banco Central...")
        selic_data = self.fetch_selic_data()
        
        ultimo_mes_completo = self._get_ultimo_mes_completo()
        print(f"Último mês completo: {ultimo_mes_completo}")
        
        # Atualizar o cache apenas com meses completos
        novos_dados = 0
        for item in selic_data:
            data_item = item.get("data", "")
            valor_item = item.get("valor", "")
            
            try:
                dt = datetime.strptime(data_item, "%d/%m/%Y")
                chave = dt.strftime("%Y-%m")
                
                # CRÍTICO: Só adicionar se for mês completo (anterior ao mês atual)
                if chave <= ultimo_mes_completo:
                    self.cache[chave] = float(valor_item)
                    novos_dados += 1
                else:
                    # Mês incompleto, ignorar
                    print(f"Ignorando mês incompleto: {chave} = {valor_item}%")
            except Exception:
                continue
        
        # Salvar cache atualizado
        self._save_cache()
        print(f"Cache atualizado com {novos_dados} meses até {ultimo_mes_completo}")
    
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
        
        # Verificar se o mês solicitado está no futuro ou é incompleto
        ultimo_mes_completo = self._get_ultimo_mes_completo()
        if mes_ano > ultimo_mes_completo:
            raise ValueError(
                f"Não é possível obter SELIC para {mes_ano}. "
                f"Último mês completo disponível: {ultimo_mes_completo}. "
                f"Aguarde o mês terminar para usar esta data."
            )
        
        # Buscar dados atualizados da API
        print(f"SELIC para {mes_ano} não encontrada no cache. Atualizando...")
        self.update_cache()
        
        # Retornar o valor solicitado
        valor = self.cache.get(mes_ano)
        if valor is None:
            raise ValueError(
                f"SELIC não disponível para {mes_ano} mesmo após atualização. "
                f"Verifique se a data está correta."
            )
        
        return valor
    
    def get_selic_for_month(self, mes_ano: str) -> Optional[float]:
        """
        Retorna o valor SELIC para um mês específico (formato: YYYY-MM).
        """
        return self.cache.get(mes_ano)
