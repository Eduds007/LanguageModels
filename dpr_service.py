"""
Serviço de retrieval real com o DPR baseline treinado em "3. Treino do DPR/".

Carrega os dois encoders treinados (query e passage), indexa as passagens de
data-5k.json (encoda cada uma com o passage_encoder, uma vez, com cache em disco)
e responde /query buscando as passagens mais similares à pergunta via produto
escalar entre embeddings — o mesmo critério usado no treino.

Requer o venv de "3. Treino do DPR/.venv" (torch, transformers, fastapi, uvicorn).

Uso:
    source "3. Treino do DPR/.venv/bin/activate"
    python dpr_service.py
"""

import json
import logging
from pathlib import Path
from typing import Optional

import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModel, AutoTokenizer

logging.basicConfig(format="%(asctime)s %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger("dpr_service")

BASE_DIR = Path(__file__).parent / "3. Treino do DPR"
MODEL_DIR = BASE_DIR / "runs" / "modified_20260826-085028" / "model"
DATA_FILE = BASE_DIR / "data-50k.json"
INDEX_CACHE = BASE_DIR / "passage_index_cache.pt"
TOP_K = 3
MAX_SEQ_LEN_QUERY = 64
MAX_SEQ_LEN_PASSAGE = 256
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    content: str


def load_passages(data_file: Path) -> list[dict]:
    with open(data_file, encoding="utf-8") as f:
        squad_data = json.load(f)
    passages = []
    for article in squad_data["data"]:
        title = article.get("title") or ""
        for paragraph in article["paragraphs"]:
            passages.append({"title": title, "text": paragraph["context"]})
    return passages


def embed_texts(texts: list[str], tokenizer, encoder, max_length: int, batch_size: int = 32) -> torch.Tensor:
    embeddings = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            tokens = tokenizer(
                batch, padding=True, truncation=True, max_length=max_length, return_tensors="pt"
            ).to(DEVICE)
            output = encoder(**tokens)
            embeddings.append(output.last_hidden_state[:, 0].cpu())
    return torch.cat(embeddings, dim=0)


class DPRIndex:
    def __init__(self):
        logger.info("Carregando encoders de %s", MODEL_DIR)
        self.query_tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR / "query_encoder")
        self.query_encoder = AutoModel.from_pretrained(MODEL_DIR / "query_encoder").to(DEVICE).eval()
        self.passage_tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR / "passage_encoder")
        self.passage_encoder = AutoModel.from_pretrained(MODEL_DIR / "passage_encoder").to(DEVICE).eval()

        self.passages = load_passages(DATA_FILE)
        self.passage_embeddings = self._load_or_build_index()

    def _load_or_build_index(self) -> torch.Tensor:
        if INDEX_CACHE.exists():
            logger.info("Carregando embeddings de passagens do cache: %s", INDEX_CACHE)
            return torch.load(INDEX_CACHE, weights_only=True)

        logger.info("Indexando %s passagens (primeira vez, pode demorar)...", len(self.passages))
        texts = [f"{p['title']} {p['text']}" for p in self.passages]
        embeddings = embed_texts(texts, self.passage_tokenizer, self.passage_encoder, MAX_SEQ_LEN_PASSAGE)
        torch.save(embeddings, INDEX_CACHE)
        logger.info("Índice salvo em %s", INDEX_CACHE)
        return embeddings

    def search(self, query: str, top_k: int = TOP_K) -> list[dict]:
        query_emb = embed_texts([query], self.query_tokenizer, self.query_encoder, MAX_SEQ_LEN_QUERY)
        scores = (query_emb @ self.passage_embeddings.T).squeeze(0)
        top_scores, top_idx = torch.topk(scores, k=min(top_k, len(self.passages)))

        results = []
        for score, idx in zip(top_scores.tolist(), top_idx.tolist()):
            passage = self.passages[idx]
            results.append(
                {
                    "answer": passage["title"] or passage["text"][:60],
                    "context": passage["text"],
                    "score": score,
                    "source": passage["title"] or "Unknown",
                }
            )
        return results


app = FastAPI()
index: Optional[DPRIndex] = None


@app.on_event("startup")
def startup():
    global index
    index = DPRIndex()
    logger.info("Índice pronto: %s passagens", len(index.passages))


@app.post("/query", response_model=QueryResponse)
def handle_query(request: QueryRequest):
    results = index.search(request.query)
    return QueryResponse(content=json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
