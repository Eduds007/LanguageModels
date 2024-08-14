from flask import Flask, request, jsonify
from haystack.nodes import DensePassageRetriever
from haystack.document_stores import ElasticsearchDocumentStore


'''
Exemplo de requisição em terminal

curl -X POST http://172.17.0.6:5000/query \
-H "Content-Type: application/json" \
-d '{"query": "O que é Python?"}'

'''

app = Flask(__name__)

# 1. Conectar à instância do Elasticsearch
document_store = ElasticsearchDocumentStore(
    host="172.17.0.5",
    port=9200,
    scheme="http",
    username="",
    password="",
    verify_certs=False,
    ca_certs="../http_ca.crt"
)

# 2. Carregar o DensePassageRetriever
save_dir = "dpr"
reloaded_retriever = DensePassageRetriever.load(load_dir=save_dir, document_store=document_store)

@app.route('/query', methods=['POST'])
def query():
    # 3. Recuperar a query do corpo da requisição
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # 4. Realizar a busca/consulta
    results = reloaded_retriever.retrieve(query)
    
    # 5. Retornar os resultados como JSON
    response = [{"content": result.content} for result in results]
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)