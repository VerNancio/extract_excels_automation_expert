import time
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

# Importando a função main do seu pacote
from src.main import main

app = FastAPI(
    title="API de Execução de Relatórios",
    description="API para substituir a execução via linha de comando.",
    version="1.0.0"
)

# Definindo o modelo de entrada com Pydantic
class ExecutionRequest(BaseModel):
    
    # Configuração no Pydantic V2 para rejeitar chaves extras
    model_config = ConfigDict(extra="forbid")
    
    # client_name não tem Optional e não tem valor padrão (None), logo é OBRIGATÓRIO
    client_name: str = Field(
        ..., 
        description="Nome da empresa"
    )
    date_to_filter: Optional[str] = Field(
        None, 
        description="Data pra filtrar no formato: dd/mm/YYYY"
    )
    date_to_save: Optional[str] = Field(
        None, 
        description="Opções: hoje / ontem / ultimo_dia_util / ultimo_dia_ultimo_mes"
    )
    save_with_date_in_name: Optional[str] = Field(
        None, 
        description="Flag ou valor para salvar com data no nome"
    )
    start_date: Optional[str] = Field(
        None, 
        description="Data inicial pra filtrar: dd/mm/YYYY"
    )
    end_date: Optional[str] = Field(
        None, 
        description="Data final pra filtrar: dd/mm/YYYY"
    )
    should_store_where: Optional[str] = Field(
        None, 
        description="Opções: local / onedrive / jestor / both"
    )
    report_type: Optional[str] = Field(
        None, 
        description="Opções: 'hour' ou 'date'"
    )


@app.post("/execute")
def execute_report(request: ExecutionRequest):
    start_time = time.time()

    # Transforma os dados recebidos em dicionário. 
    # exclude_none=True garante que chaves não enviadas não sejam passadas para a função main()
    kwargs = request.model_dump(exclude_none=True)

    try:
        # Executa a função passando o dicionário desempacotado
        exec_succeded: tuple[int, bool] | bool = main(**kwargs)
    except Exception as e:
        # Se a main() der erro, a API retorna status 500 informando o que falhou
        raise HTTPException(status_code=500, detail=f"Erro interno na execução: {str(e)}")

    end_time = time.time()
    execution_time = round(end_time - start_time, 2)

    if not exec_succeded:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Execução falhou internamente.",
                "execution_time_seconds": execution_time,
                "parameters_used": kwargs
            }
        )

    # Se não for falso, é uma tupla com a quantidade de registros salvos e se foram todos salvos
    rows_saved = exec_succeded[0]
    all_rows_were_stored =  exec_succeded[1]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Execução finalizada com sucesso.",
            "execution_time_seconds": execution_time,
            "qnt_rows_stored": rows_saved,
            "all_rows_were_stored": all_rows_were_stored,
            "parameters_used": kwargs
        }
    )
        
    
# --- BLOCO ADICIONADO PARA RODAR O SERVIDOR ---
if __name__ == "__main__":
    print("Iniciando o servidor FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=8000, ws="none")