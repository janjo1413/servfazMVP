"""
API FastAPI - Endpoint principal /calculate

FLUXO:
1. Recebe dados do frontend (conforme schema_input.json)
2. Valida a data de correção e busca SELIC se necessário
3. Escreve dados na planilha Excel (aba RESUMO)
4. Executa app.calculate() via xlwings
5. Lê as tabelas vermelhas (linhas 21-104, colunas A-F e AB)
6. Salva input + output no SQLite
7. Retorna JSON com id + resultados (conforme schema_output.json)

DECISÕES TÉCNICAS:
- FastAPI para API moderna e rápida
- CORS habilitado para desenvolvimento local
- Validação automática via Pydantic
- Context manager para garantir fechamento do Excel
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from pathlib import Path
import os
import sys

# Adicionar o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from database import init_database
from services.excel_runner import ExcelRunner
from services.selic_api import SelicAPI
from services.selic_updater import SelicUpdater


# Configuração de caminhos
BASE_DIR = Path(__file__).parent.parent
EXCEL_PATH = os.getenv("EXCEL_FILE_PATH", str(BASE_DIR / "data" / "planilhamae.xlsx"))
MAPA_CELULAS_PATH = str(BASE_DIR / "data" / "mapa_celulas.json")
DATABASE_PATH = os.getenv("DATABASE_URL", str(BASE_DIR / "data" / "results.db")).replace("sqlite:///", "")
SELIC_CACHE_PATH = str(BASE_DIR / "data" / "selic_cache.json")


# Modelos Pydantic (baseados nos schemas)
class CalculateInput(BaseModel):
    município: str = Field(..., description="Nome do município")
    ajuizamento: str = Field(..., description="Data de ajuizamento")
    citação: str = Field(..., description="Data de citação")
    início_cálculo: str = Field(..., description="Data de início do cálculo")
    final_cálculo: str = Field(..., description="Data final do cálculo")
    honorários_s_valor_da_condenação: float = Field(..., description="Percentual de honorários")
    honorários_em_valor_fixo: float = Field(..., description="Valor fixo de honorários")
    deságio_a_aplicar_sobre_o_principal: float = Field(..., description="Percentual de deságio no principal")
    deságio_em_a_aplicar_em_honorários: float = Field(..., description="Percentual de deságio em honorários")
    correção_até: str = Field(..., description="Data de correção")


class TableBlock(BaseModel):
    titulo: str
    header: List[str]
    rows: List[List[Any]]
    total: Optional[List[Any]] = None


class CalculateResult(BaseModel):
    id: str
    created_at: str
    correcao_ate: str
    results_base: List[TableBlock]  # Resultados fixos da planilha (01/01/2025)
    results_atualizados: Optional[List[TableBlock]] = None  # Resultados com SELIC aplicada (se data > 01/01/2025)


# Inicialização do FastAPI
app = FastAPI(
    title="ServFaz MVP - Excel Calculator API",
    description="API que usa Excel como motor de cálculo para processos jurídicos",
    version="1.0.0"
)

# CORS (permitir requisições do frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar banco de dados
storage = init_database(DATABASE_PATH)
selic_api = SelicAPI(SELIC_CACHE_PATH)
selic_updater = SelicUpdater(SELIC_CACHE_PATH)


@app.get("/")
def root():
    """Endpoint de health check."""
    return {
        "status": "online",
        "service": "ServFaz MVP",
        "excel_path": EXCEL_PATH,
        "database_path": DATABASE_PATH
    }


@app.post("/calculate", response_model=CalculateResult)
def calculate(input_data: CalculateInput):
    """
    Endpoint principal de cálculo.
    
    1. Recebe dados do formulário
    2. Valida SELIC para a data de correção
    3. Escreve na planilha e executa cálculo
    4. Lê resultados das tabelas vermelhas
    5. Salva no banco e retorna JSON
    """
    try:
        # 1. Validar e garantir dados SELIC
        print(f"📅 Validando SELIC para: {input_data.correção_até}")
        try:
            selic_value = selic_api.ensure_selic(input_data.correção_até)
            if selic_value:
                print(f"SELIC encontrada: {selic_value}%")
        except Exception as selic_error:
            print(f"⚠️ Aviso SELIC: {str(selic_error)}")
            # Continuar mesmo sem SELIC (planilha pode ter dados suficientes)
        
        # 2. Executar cálculo no Excel
        print(f"Abrindo Excel: {EXCEL_PATH}")
        
        with ExcelRunner(EXCEL_PATH, MAPA_CELULAS_PATH) as runner:
            # Escrever inputs
            print("✏️ Escrevendo dados na planilha...")
            runner.write_inputs(input_data.dict())
            
            # Calcular
            print("Executando cálculo...")
            runner.calculate()
            
            # Ler resultados
            print("📖 Lendo resultados das tabelas...")
            results = runner.read_results()
        
        print(f"{len(results)} blocos de tabela lidos com sucesso")
        
        # 3. Aplicar atualização SELIC (se data > 01/01/2025)
        results_atualizados = None
        if selic_updater.precisa_atualizacao(input_data.correção_até):
            print(f"Aplicando atualização SELIC para {input_data.correção_até}...")
            results_atualizados = selic_updater.atualizar_resultados(results, input_data.correção_até)
            print(f"Resultados atualizados com SELIC gerados")
        else:
            print(f"Data de correção ≤ 01/01/2025. Sem atualização SELIC.")
        
        # 4. Preparar resposta
        created_at = datetime.now().isoformat()
        
        output_data = {
            "results_base": results,
            "results_atualizados": results_atualizados,
            "correcao_ate": input_data.correção_até
        }
        
        # 5. Salvar no banco
        print("💾 Salvando no banco de dados...")
        result_id = storage.save_result(
            input_data=input_data.dict(),
            output_data=output_data
        )
        
        # 6. Retornar resposta
        response = {
            "id": result_id,
            "created_at": created_at,
            "correcao_ate": input_data.correção_até,
            "results_base": results,
            "results_atualizados": results_atualizados
        }
        
        print(f"🎉 Cálculo concluído! ID: {result_id}")
        
        return response
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=f"Planilha não encontrada: {EXCEL_PATH}"
        )
    except Exception as e:
        print(f"Erro no cálculo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar cálculo: {str(e)}"
        )


@app.get("/results/{result_id}")
def get_result(result_id: str):
    """
    Recupera um resultado específico pelo ID.
    """
    result = storage.get_result(result_id)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Resultado não encontrado: {result_id}"
        )
    
    return result


@app.get("/results")
def list_results(limit: int = 100):
    """
    Lista os últimos resultados salvos.
    """
    results = storage.list_results(limit=limit)
    return {"results": results, "count": len(results)}


@app.delete("/results/{result_id}")
def delete_result(result_id: str):
    """
    Deleta um resultado específico pelo ID.
    """
    success = storage.delete_result(result_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Resultado não encontrado: {result_id}"
        )
    
    return {"message": f"Resultado {result_id} deletado com sucesso"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
