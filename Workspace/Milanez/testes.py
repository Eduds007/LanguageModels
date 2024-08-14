from haystack.nodes import DensePassageRetriever
from haystack.document_stores import ElasticsearchDocumentStore


print('1. Connect to your Elasticsearch instance')
document_store = ElasticsearchDocumentStore(
    host="localhost",  # Adjust according to your Elasticsearch setup
    username="",
    password="",
    index="document",
    port=9200
)

print('2. Load the DensePassageRetriever')
save_dir = "dpr"
reloaded_retriever = DensePassageRetriever.load(load_dir=save_dir, document_store=None)

print(' 3. Assign the retriever to the document store')
document_store.retriever = reloaded_retriever

# 4. Write documents to the ElasticsearchDocumentStore (if not already written)
#docs = [
#    {"content": "This is a document about Python."},
#    {"content": "This is another document about machine learning."},
#    # Add more documents as needed
#]
#document_store.write_documents(docs)

print('5. Update embeddings in the ElasticsearchDocumentStore')
document_store.update_embeddings(retriever=reloaded_retriever)

print(' 6. Perform a search/query')

query = "O que é Python?"
results = reloaded_retriever.retrieve(query)
for result in results:
    print(result.content)
