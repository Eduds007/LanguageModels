import logging


from haystack.nodes import DensePassageRetriever
from haystack.utils import fetch_archive_from_http
from haystack.document_stores import ElasticsearchDocumentStore


logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

#separar aqui o json de treino e de dev
train_filename = "data-5k.json"
dev_filename = "data-5k.json"

query_model = "bert-base-uncased"
passage_model = "bert-base-uncased"

save_dir = "../saved_models/dpr"
doc_dir = ""

retriever = DensePassageRetriever(
    document_store=ElasticsearchDocumentStore(),
    query_embedding_model=query_model,
    passage_embedding_model=passage_model,
    max_seq_len_query=64,
    max_seq_len_passage=256,
)

retriever.train(
    data_dir=doc_dir,
    train_filename=train_filename,
    dev_filename=dev_filename,
    test_filename=dev_filename,
    n_epochs=1,
    batch_size=16,
    grad_acc_steps=8,
    save_dir=save_dir,
    evaluate_every=3000,
    embed_title=True,
    num_positives=1,
    num_hard_negatives=1,
)