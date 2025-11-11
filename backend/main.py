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
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

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
    title="JGJPRC MVP - Excel Calculator API",
    description="API que usa Excel como motor de cálculo para processos jurídicos",
    version="1.0.0"
)

# CORS (permitir requisições do frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Permitir todas as origens (desenvolvimento)
        "https://jg-jp-rc-mvp.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar banco de dados
storage = init_database(DATABASE_PATH)
selic_api = SelicAPI(SELIC_CACHE_PATH)
selic_updater = SelicUpdater(SELIC_CACHE_PATH)


# ============================================================================
# SCHEDULER - Atualização automática de SELIC
# ============================================================================
def atualizar_selic_agendado():
    """
    Tarefa agendada que atualiza o cache de SELIC diariamente.
    Executa todo dia às 6h da manhã.
    """
    print("=" * 60)
    print(f"[SCHEDULER] Executando atualização automática de SELIC - {datetime.now()}")
    print("=" * 60)
    try:
        selic_api.update_cache()
        print("[SCHEDULER] Cache SELIC atualizado com sucesso!")
    except Exception as e:
        print(f"[SCHEDULER] Erro ao atualizar SELIC: {str(e)}")
    print("=" * 60)


# Criar scheduler em background
scheduler = BackgroundScheduler()

# Agendar atualização diária às 6h da manhã (horário de Brasília)
scheduler.add_job(
    func=atualizar_selic_agendado,
    trigger=CronTrigger(hour=6, minute=0),  # Todo dia às 06:00
    id='atualizar_selic',
    name='Atualização automática de SELIC',
    replace_existing=True
)

# Iniciar scheduler
scheduler.start()
print("[SCHEDULER] Scheduler iniciado - Atualização automática de SELIC agendada para 06:00 diariamente")

# Garantir que o scheduler seja desligado corretamente ao encerrar a aplicação
atexit.register(lambda: scheduler.shutdown())
# ============================================================================


@app.get("/")
def root():
    """Endpoint de health check."""
    # Obter informações sobre o próximo agendamento
    proxima_atualizacao = None
    jobs = scheduler.get_jobs()
    if jobs:
        proxima_atualizacao = jobs[0].next_run_time.isoformat() if jobs[0].next_run_time else None
    
    return {
        "status": "online",
        "service": "RcJgJp MVP",
        "excel_path": EXCEL_PATH,
        "database_path": DATABASE_PATH,
        "scheduler": {
            "ativo": scheduler.running,
            "proxima_atualizacao_selic": proxima_atualizacao
        }
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
        # 1. Validar e garantir dados SELIC (OBRIGATÓRIO para datas > 01/01/2025)
        print(f"Validando SELIC para: {input_data.correção_até}")
        
        # Verificar se precisa de SELIC da API (data > 01/01/2025)
        if selic_updater.precisa_atualizacao(input_data.correção_até):
            # CRÍTICO: Planilha tem SELIC fixa (1.00%) após 01/01/2025
            # Sistema DEVE buscar valores reais da API
            try:
                selic_value = selic_api.ensure_selic(input_data.correção_até)
                if selic_value:
                    print(f"SELIC encontrada: {selic_value}%")
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"SELIC não encontrada para {input_data.correção_até}. Não é possível calcular sem dados SELIC atualizados."
                    )
            except HTTPException:
                raise  # Re-lançar HTTPException
            except Exception as selic_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao buscar SELIC: {str(selic_error)}. Sistema não pode continuar sem SELIC atualizada para datas > 01/01/2025."
                )
        else:
            print(f"Data ≤ 01/01/2025. Usando dados da planilha (sem SELIC adicional)")
        
        # 2. Executar cálculo no Excel
        print(f"Abrindo Excel: {EXCEL_PATH}")
        
        with ExcelRunner(EXCEL_PATH, MAPA_CELULAS_PATH) as runner:
            # Escrever inputs
            print("Escrevendo dados na planilha...")
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
            try:
                results_atualizados = selic_updater.atualizar_resultados(results, input_data.correção_até)
                print(f"Resultados atualizados com SELIC gerados")
            except ValueError as selic_error:
                # Erro ao aplicar SELIC (falta de dados)
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro na atualização SELIC: {str(selic_error)}"
                )
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


@app.delete("/results")
def delete_all_results():
    """
    Deleta TODOS os resultados do banco de dados.
    ATENÇÃO: Operação irreversível! Uso temporário para testes.
    """
    try:
        count = storage.delete_all_results()
        return {
            "message": f"Todos os cálculos foram deletados com sucesso",
            "total_deletados": count
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar todos os resultados: {str(e)}"
        )


@app.get("/selic/ultima-data")
def get_ultima_data_selic():
    """
    Retorna a última data de SELIC disponível no cache.
    """
    try:
        # Buscar último mês no cache
        meses = list(selic_api.cache.keys())
        if not meses:
            raise HTTPException(
                status_code=500,
                detail="Cache SELIC vazio. Execute a atualização da API."
            )
        
        # Ordenar e pegar o último
        meses.sort()
        ultimo_mes = meses[-1]  # Formato: "YYYY-MM"
        
        # Converter para DD/MM/YYYY (sempre dia 01)
        ano, mes = ultimo_mes.split('-')
        ultima_data = f"01/{mes}/{ano}"
        
        return {
            "ultima_data": ultima_data,
            "mes": ultimo_mes,
            "taxa": selic_api.cache[ultimo_mes]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar última data SELIC: {str(e)}"
        )


@app.get("/selic/status")
def get_selic_status():
    """
    Retorna informações completas sobre o cache de SELIC e scheduler.
    Inclui lista dos últimos 12 meses com suas respectivas taxas.
    """
    try:
        # Informações do cache
        meses = [k for k in selic_api.cache.keys() if k != '_metadata']
        meses.sort()
        
        total_meses = len(meses)
        primeiro_mes = meses[0] if meses else None
        ultimo_mes = meses[-1] if meses else None
        
        # Metadata
        last_update = selic_api.cache_metadata.get('last_update')
        
        # Próxima atualização agendada
        proxima_atualizacao = None
        jobs = scheduler.get_jobs()
        if jobs:
            proxima_atualizacao = jobs[0].next_run_time.isoformat() if jobs[0].next_run_time else None
        
        # Últimos 12 meses com taxas (apenas a partir de 2025-01)
        ultimos_12_meses = []
        if meses:
            # Filtrar apenas meses >= 2025-01
            meses_desde_2025 = [m for m in meses if m >= '2025-01']
            meses_recentes = meses_desde_2025[-12:] if len(meses_desde_2025) > 12 else meses_desde_2025
            for mes in meses_recentes:
                ultimos_12_meses.append({
                    "mes": mes,
                    "taxa": selic_api.cache.get(mes)
                })
        
        return {
            "cache": {
                "total_meses": total_meses,
                "primeiro_mes": primeiro_mes,
                "ultimo_mes": ultimo_mes,
                "ultima_atualizacao": last_update,
                "taxa_ultimo_mes": selic_api.cache.get(ultimo_mes) if ultimo_mes else None
            },
            "scheduler": {
                "ativo": scheduler.running,
                "proxima_atualizacao": proxima_atualizacao,
                "horario_agendado": "06:00 (diariamente)"
            },
            "ultimos_12_meses": ultimos_12_meses
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar status SELIC: {str(e)}"
        )
        
        # Próxima atualização agendada
        proxima_atualizacao = None
        jobs = scheduler.get_jobs()
        if jobs:
            proxima_atualizacao = jobs[0].next_run_time.isoformat() if jobs[0].next_run_time else None
        
        return {
            "cache": {
                "total_meses": total_meses,
                "primeiro_mes": primeiro_mes,
                "ultimo_mes": ultimo_mes,
                "ultima_atualizacao": last_update,
                "taxa_ultimo_mes": selic_api.cache.get(ultimo_mes) if ultimo_mes else None
            },
            "scheduler": {
                "ativo": scheduler.running,
                "proxima_atualizacao": proxima_atualizacao,
                "horario_agendado": "06:00 (diariamente)"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar status SELIC: {str(e)}"
        )


@app.post("/selic/forcar-atualizacao")
def forcar_atualizacao_selic():
    """
    Força atualização imediata do cache de SELIC (não precisa esperar o agendamento).
    """
    try:
        print("Atualização manual de SELIC solicitada via API")
        selic_api.update_cache()
        
        # Retornar status atualizado
        meses = [k for k in selic_api.cache.keys() if k != '_metadata']
        meses.sort()
        ultimo_mes = meses[-1] if meses else None
        
        return {
            "status": "sucesso",
            "mensagem": "Cache SELIC atualizado com sucesso",
            "total_meses": len(meses),
            "ultimo_mes": ultimo_mes,
            "taxa_ultimo_mes": selic_api.cache.get(ultimo_mes) if ultimo_mes else None,
            "atualizado_em": selic_api.cache_metadata.get('last_update')
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao forçar atualização SELIC: {str(e)}"
        )


@app.post("/results/{result_id}/atualizar")
def atualizar_resultado(result_id: str):
    """
    Atualiza um resultado existente para a última data SELIC disponível.
    
    1. Busca o resultado original
    2. Verifica a última data SELIC disponível
    3. Se já está atualizado, retorna erro
    4. Caso contrário, recalcula com a nova data
    5. Atualiza o registro mantendo created_at original
    """
    try:
        # 1. Buscar resultado original
        resultado = storage.get_result(result_id)
        
        if not resultado:
            raise HTTPException(
                status_code=404,
                detail=f"Resultado não encontrado: {result_id}"
            )
        
        # 2. Buscar última data SELIC
        meses = list(selic_api.cache.keys())
        if not meses:
            raise HTTPException(
                status_code=500,
                detail="Cache SELIC vazio"
            )
        
        meses.sort()
        ultimo_mes = meses[-1]
        ano, mes = ultimo_mes.split('-')
        ultima_data_selic = f"01/{mes}/{ano}"
        
        # 3. Verificar se já está atualizado
        correcao_atual = resultado['output_data'].get('correcao_ate')
        
        if correcao_atual == ultima_data_selic:
            raise HTTPException(
                status_code=400,
                detail=f"Cálculo já está atualizado para o mês mais recente ({mes}/{ano})"
            )
        
        # 4. Recalcular com nova data
        input_data = resultado['input_data']
        input_data['correção_até'] = ultima_data_selic
        
        print(f"Atualizando cálculo {result_id} de {correcao_atual} para {ultima_data_selic}")
        
        # Executar cálculo no Excel (mesmos inputs, só muda data de correção)
        with ExcelRunner(EXCEL_PATH, MAPA_CELULAS_PATH) as runner:
            runner.write_inputs(input_data)
            runner.calculate()
            results = runner.read_results()
        
        # Aplicar SELIC atualizada
        results_atualizados = None
        if selic_updater.precisa_atualizacao(ultima_data_selic):
            try:
                results_atualizados = selic_updater.atualizar_resultados(results, ultima_data_selic)
            except ValueError as selic_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro na atualização SELIC: {str(selic_error)}"
                )
        
        # 5. Preparar novo output_data com histórico
        novo_output_data = {
            "results_base": results,
            "results_atualizados": results_atualizados,
            "correcao_ate": ultima_data_selic,
            "correcao_anterior": correcao_atual  # Guardar data anterior
        }
        
        # 6. Atualizar no banco (mantém created_at, atualiza updated_at)
        success = storage.update_result(result_id, novo_output_data)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Falha ao atualizar resultado no banco"
            )
        
        print(f"Cálculo {result_id} atualizado com sucesso!")
        
        # 7. Retornar resultado atualizado
        resultado_atualizado = storage.get_result(result_id)
        
        return {
            "message": "Cálculo atualizado com sucesso",
            "data_anterior": correcao_atual,
            "data_nova": ultima_data_selic,
            "resultado": resultado_atualizado
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao atualizar resultado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar cálculo: {str(e)}"
        )


@app.post("/results/atualizar-todos")
def atualizar_todos_resultados():
    """
    Atualiza TODOS os cálculos para a última data SELIC disponível.
    
    Processa cada cálculo individualmente e retorna relatório completo:
    - Sucessos: lista de IDs atualizados
    - Erros: lista de IDs que falharam e motivo
    - Já atualizados: lista de IDs que já estavam na data mais recente
    """
    try:
        # 1. Buscar todos os resultados
        todos_calculos = storage.list_all_results()
        
        if not todos_calculos:
            return {
                "message": "Nenhum cálculo encontrado para atualizar",
                "total": 0,
                "sucessos": [],
                "erros": [],
                "ja_atualizados": []
            }
        
        # 2. Buscar última data SELIC
        meses = [k for k in selic_api.cache.keys() if k != '_metadata']
        if not meses:
            raise HTTPException(
                status_code=500,
                detail="Cache SELIC vazio"
            )
        
        meses.sort()
        ultimo_mes = meses[-1]
        ano, mes = ultimo_mes.split('-')
        ultima_data_selic = f"01/{mes}/{ano}"
        
        print(f"=" * 60)
        print(f"Iniciando atualização em lote para {ultima_data_selic}")
        print(f"Total de cálculos: {len(todos_calculos)}")
        print(f"=" * 60)
        
        # 3. Processar cada cálculo
        sucessos = []
        erros = []
        ja_atualizados = []
        
        for i, calculo in enumerate(todos_calculos, 1):
            calculo_id = calculo['id']
            
            try:
                print(f"[{i}/{len(todos_calculos)}] Processando {calculo_id}...")
                
                # Verificar se já está atualizado
                resultado = storage.get_result(calculo_id)
                correcao_atual = resultado['output_data'].get('correcao_ate') or resultado['input_data'].get('correção_até')
                
                if correcao_atual == ultima_data_selic:
                    print(f"  [OK] Já atualizado")
                    ja_atualizados.append({
                        "id": calculo_id,
                        "municipio": resultado['input_data'].get('município', 'N/A')
                    })
                    continue
                
                # Recalcular
                input_data = resultado['input_data'].copy()
                input_data['correção_até'] = ultima_data_selic
                
                with ExcelRunner(EXCEL_PATH, MAPA_CELULAS_PATH) as runner:
                    runner.write_inputs(input_data)
                    runner.calculate()
                    results = runner.read_results()
                
                # Aplicar SELIC
                results_atualizados = None
                if selic_updater.precisa_atualizacao(ultima_data_selic):
                    results_atualizados = selic_updater.atualizar_resultados(results, ultima_data_selic)
                
                # Atualizar banco
                novo_output_data = {
                    "results_base": results,
                    "results_atualizados": results_atualizados,
                    "correcao_ate": ultima_data_selic,
                    "correcao_anterior": correcao_atual
                }
                
                storage.update_result(calculo_id, novo_output_data)
                
                print(f"  [OK] Atualizado: {correcao_atual} -> {ultima_data_selic}")
                sucessos.append({
                    "id": calculo_id,
                    "municipio": input_data.get('município', 'N/A'),
                    "data_anterior": correcao_atual,
                    "data_nova": ultima_data_selic
                })
                
            except Exception as e:
                print(f"  [ERRO] Erro: {str(e)}")
                erros.append({
                    "id": calculo_id,
                    "municipio": calculo.get('município', 'N/A'),
                    "erro": str(e)
                })
        
        print(f"=" * 60)
        print(f"Atualização em lote concluída!")
        print(f"Sucessos: {len(sucessos)} | Erros: {len(erros)} | Já atualizados: {len(ja_atualizados)}")
        print(f"=" * 60)
        
        return {
            "message": "Atualização em lote concluída",
            "total": len(todos_calculos),
            "sucessos": sucessos,
            "erros": erros,
            "ja_atualizados": ja_atualizados,
            "data_selic": ultima_data_selic
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro na atualização em lote: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na atualização em lote: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
