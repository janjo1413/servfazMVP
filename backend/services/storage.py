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
                updated_at TEXT,
                input_data TEXT NOT NULL,
                output_data TEXT NOT NULL
            )
        """)
        
        # Adicionar coluna updated_at em bancos existentes (migration)
        cursor.execute("PRAGMA table_info(results)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE results ADD COLUMN updated_at TEXT")
        
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
            Dicionário com id, created_at, updated_at, input_data, output_data ou None
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, created_at, updated_at, input_data, output_data FROM results WHERE id = ?",
            (result_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "created_at": row[1],
                "updated_at": row[2],
                "input_data": json.loads(row[3]),
                "output_data": json.loads(row[4])
            }
        
        return None
    
    def list_results(self, limit: int = 100) -> list:
        """
        Lista os últimos resultados salvos.
        
        Args:
            limit: Número máximo de resultados a retornar
        
        Returns:
            Lista de dicionários com id, created_at, updated_at, input_data (resumido)
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, created_at, updated_at, input_data, output_data FROM results ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            input_data = json.loads(row[3])
            output_data = json.loads(row[4]) if row[4] else {}
            
            # Pegar correção atualizada do output_data se existir, senão usar input_data
            correcao_ate = output_data.get('correcao_ate') or input_data.get("correção_até", "N/A")
            correcao_anterior = output_data.get('correcao_anterior')
            
            results.append({
                "id": row[0],
                "created_at": row[1],
                "updated_at": row[2],
                "município": input_data.get("município", "N/A"),
                "correção_até": input_data.get("correção_até", "N/A"),  # Original
                "correcao_ate": correcao_ate,  # Atualizada
                "correcao_anterior": correcao_anterior  # Data anterior (se foi atualizado)
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
    
    def delete_all_results(self) -> int:
        """
        Deleta TODOS os resultados do banco de dados.
        ATENÇÃO: Operação irreversível!
        
        Returns:
            Número de resultados deletados
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM results")
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
    
    def list_all_results(self) -> list:
        """
        Lista TODOS os resultados completos do banco (sem limite).
        Usado para operações em lote.
        
        Returns:
            Lista de dicionários com todos os campos
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, created_at, updated_at, input_data, output_data FROM results ORDER BY created_at DESC"
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            input_data = json.loads(row[3])
            output_data = json.loads(row[4]) if row[4] else {}
            
            results.append({
                "id": row[0],
                "created_at": row[1],
                "updated_at": row[2],
                "município": input_data.get("município", "N/A"),
                "input_data": input_data,
                "output_data": output_data
            })
        
        return results
    
    def update_result(self, result_id: str, output_data: Dict[str, Any]) -> bool:
        """
        Atualiza apenas o output_data de um resultado existente.
        Mantém created_at original e atualiza updated_at.
        
        Args:
            result_id: ID do resultado a atualizar
            output_data: Novos dados de saída
        
        Returns:
            True se atualizado com sucesso, False se não encontrado
        """
        updated_at = datetime.now().isoformat()
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE results SET output_data = ?, updated_at = ? WHERE id = ?",
            (
                json.dumps(output_data, ensure_ascii=False),
                updated_at,
                result_id
            )
        )
        
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return updated
