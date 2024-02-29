## Tatudo bugado, tenho q fazeer ainda

from haystack.nodes import PromptTemplate, PromptNode, PromptModel
from haystack.pipelines import Pipeline
from haystack.retriever.sparse import BM25Retriever
from haystack.document_store.memory import InMemoryDocumentStore
from haystack.document_store.faiss import FAISSDocumentStore
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.document_store.sql import SQLDocumentStore
from haystack.document_store.milvus import MilvusDocumentStore
from haystack.document_store.weaviate import WeaviateDocumentStore
from haystack.document_store.memory import InMemoryDocumentStore
from haystack.document_store.faiss import FAISSDocumentStore
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.document_store.sql import SQLDocumentStore
from haystack.document_store.milvus import MilvusDocumentStore
from haystack.document_store.weaviate import WeaviateDocumentStore

documents = [{"text": "Berlin is the capital of Germany"}]

document_store = InMemoryDocumentStore()

document_store.write_documents(documents)

bm25_retriever = BM25Retriever(document_store=document_store)

model_path = "path/to/your/model"
prompt_model = PromptModel(model_name_or_path=model_path)

node_prompt = PromptNode(prompt_model, default_prompt_template="deepset/question-generation", output_variable="questions")

pipeline = Pipeline()
pipeline.add_node(component=bm25_retriever, name="BM25Retriever", inputs=["Query"])
pipeline.add_node(component=node_prompt, name="prompt_node", inputs=["BM25Retriever"])

output = pipeline.run(query="not relevant")
print(output["results"])