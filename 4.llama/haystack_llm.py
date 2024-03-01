from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import PromptNode, PromptTemplate, BM25Retriever
from haystack import Pipeline, Agent
import json


#Erro 

# Configuração do armazenamento de documentos
print("Carregando Document Store")
document_store = InMemoryDocumentStore(use_bm25=True)
file = "docs.json"
with open(file, encoding='utf-8') as json_file:
    hdocs = json.load(json_file)
document_store.write_documents(hdocs, duplicate_documents='overwrite')
print("Document Store carregada")

# BM25 Retriever
print("Carregando Retriever  ...")
retriever = BM25Retriever(document_store=document_store, top_k=7)
print("Retriever Carregado !")

# Configuração do PromptNode e PromptTemplate- QA
QA_promptnode = PromptTemplate(
    prompt="Responda a pergunta baseando-se nos documentos fornecidos. Pergunta: {query}. Resposta:",
)
QA_builder = PromptNode(
    model_name_or_path="text-davinci-003",
    api_key="TEM-QUE-TER-UMA-CHAVE-DE-API-É-SÓ-SE-CADASTRAR-NO-SITE-DA-OPENAI-E-PEGAR-A-CHAVE: https://beta.openai.com/signup/",
    default_prompt_template=QA_promptnode
)

# Configuração da Pipeline
pipeline = Pipeline()
pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
pipeline.add_node(component=QA_builder, name="Responder", inputs=["Retriever"])

# Configuração do Agente
agent_prompt_node = PromptNode(
    model_name_or_path="gpt-3.5-turbo",
    api_key="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",
    max_length=512,
    stop_words=["Observation:"],
    model_kwargs={"temperature": 0.2},
)
agent_template = PromptTemplate(
    prompt="EDUsIA está pronto para responder às suas perguntas. Faça uma pergunta:",
)

EDUsIA = Agent(
    prompt_node=agent_prompt_node,
    prompt_template=agent_template,
)
EDUsIA.add_tool(retriever)
print("EDUsIA Pronto")

while True:
    print('\n')
    query = input("Pergunte algo:")
    print(pipeline.run(query=query))
