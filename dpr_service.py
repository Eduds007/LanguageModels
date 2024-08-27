from fastapi import FastAPI
from pydantic import BaseModel
import json
from time import sleep

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    content: str

@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    # Simulando uma resposta baseada na query
    sleep(3)
    response_content = """
    [
       {
          "answer":"interpretador",
          "context":"O cliente Qt é escrito em Python, mas não está disponível como um download oficial, desde de agosto de 2009. Ambiente de desenvolvimento - Não existe ",
          "score":0.6796301007270813,
          "source":"Unknown"
       },
       {
          "answer":"Duck typing",
          "context":" o grupo de notícias comp.lang.python: - Implementações - Em Python - Duck typing é muito usado em Python, com o exemplo canônico sendo classes semelh",
          "score":0.5904070138931274,
          "source":"Unknown"
       },
       {
          "answer":"interpretador",
          "context":"Console Python integrado: O interpretador Python inclui realce de sintaxe, autocompletar, e navegador de classes. Comandos Python podem ser inseridos ",
          "score":0.5705952048301697,
          "source":"Unknown"
       }
    ]
    """
    return QueryResponse(content=response_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)