"""
Camada de persistência de dados no SQLite.
Armazena input, output e metadados de cada cálculo realizado.

DECISÕES TÉCNICAS:
- SQLite para simplicidade (sem necessidade de servidor externo)
- Tabela 'results' com id, created_at, input_data, output_data
- JSON serializado para flexibilidade nos dados
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


class Storage:
    """
    Gerencia a persistência dos cálculos no banco SQLite.
    """
    
    def __init__(self, db_path: str = "./data/results.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self) -> None:
        """Cria a tabela 'results' se não existir."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                input_data TEXT NOT NULL,
                output_data TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_result(self, input_data: Dict[str, Any], output_data: Dict[str, Any]) -> str:
        """
        Salva um resultado de cálculo no banco.
        
        Args:
            input_data: Dados de entrada (conforme schema_input.json)
            output_data: Dados de saída (conforme schema_output.json)
        
        Returns:
            ID único do registro
        """
        result_id = str(uuid.uuid4())
        # Usar horário local do sistema ao invés de UTC
        created_at = datetime.now().isoformat()
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO results (id, created_at, input_data, output_data) VALUES (?, ?, ?, ?)",
            (
                result_id,
                created_at,
                json.dumps(input_data, ensure_ascii=False),
                json.dumps(output_data, ensure_ascii=False)
            )
        )
        
        conn.commit()
        conn.close()
        
        return result_id
    
    def get_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera um resultado pelo ID.
        
        Returns:
            Dicionário com id, created_at, input_data, output_data ou None
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, created_at, input_data, output_data FROM results WHERE id = ?",
            (result_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "created_at": row[1],
                "input_data": json.loads(row[2]),
                "output_data": json.loads(row[3])
            }
        
        return None
    
    def list_results(self, limit: int = 100) -> list:
        """
        Lista os últimos resultados salvos.
        
        Args:
            limit: Número máximo de resultados a retornar
        
        Returns:
            Lista de dicionários com id, created_at, input_data (resumido)
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, created_at, input_data FROM results ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            input_data = json.loads(row[2])
            results.append({
                "id": row[0],
                "created_at": row[1],
                "município": input_data.get("município", "N/A"),
                "correção_até": input_data.get("correção_até", "N/A")
            })
        
        return results
    
    def delete_result(self, result_id: str) -> bool:
        """
        Deleta um resultado pelo ID.
        
        Args:
            result_id: ID do resultado a deletar
        
        Returns:
            True se deletado com sucesso, False se não encontrado
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
