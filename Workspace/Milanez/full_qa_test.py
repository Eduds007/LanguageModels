from haystack.nodes import DensePassageRetriever
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import FARMReader
from haystack.pipelines import ExtractiveQAPipeline
from pprint import pprint
from haystack.utils import print_answers

print('1. Connect to your Elasticsearch instance')

document_store = ElasticsearchDocumentStore(
    host="172.17.0.5",
    port=9200,
    scheme="http",  # Use "http" or "https" based on your Elasticsearch configuration
    username="",  # Add your username if necessary
    password="",  # Add your password if necessary
    verify_certs=False,  # Add this if you want to bypass certificate verification
    ca_certs="../http_ca.crt"  # Path to your CA certificate file
)

print('2. Load the DensePassageRetriever')
save_dir = "dpr"
reloaded_retriever = DensePassageRetriever.load(load_dir=save_dir, document_store=document_store)


reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)
pipe = ExtractiveQAPipeline(reader, reloaded_retriever)

prediction = pipe.run(
    query="Who is the father of Arya Stark?", params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 5}}
)

pprint(prediction)
print_answers(prediction, details="minimum")