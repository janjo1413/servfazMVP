"""
Configuração do banco de dados SQLite.
Inicializa a estrutura e fornece conexão.

DECISÕES TÉCNICAS:
- SQLite como banco local
- Estrutura simples para MVP
- Criação automática de tabelas no startup
"""

from pathlib import Path
from services.storage import Storage


def init_database(db_path: str = "./data/results.db") -> Storage:
    """
    Inicializa o banco de dados e retorna uma instância do Storage.
    
    Args:
        db_path: Caminho para o arquivo do banco SQLite
    
    Returns:
        Instância do Storage
    """
    storage = Storage(db_path)
    print(f"Banco de dados inicializado: {db_path}")
    return storage
