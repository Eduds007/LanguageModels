"""
Treino do DPR (Dense Passage Retriever): dois encoders BERT-like (query e passage),
treinados para colocar pergunta e passagem certa próximas no espaço de embeddings
(dot product), usando NLL loss sobre o positivo + negativos difíceis + negativos
"in-batch" — a mesma formulação do paper original (Karpukhin et al., 2020).

Implementado direto em torch/transformers (sem Haystack): a versão do Haystack
usada originalmente no repositório (farm-haystack, sem atualização desde ~2024) não
é mais compatível com as versões atuais (2026) de transformers/numpy/scipy.

Pipeline completo:
    1. Converter o dataset SQuAD-like para o formato DPR:

           python squad_to_dpr.py --squad_input_filename data-5k.json \
               --dpr_output_filename data-5k-dpr.json --split_dataset

       Isso gera data-5k-dpr.train.json / .dev.json / .test.json. Repita para
       data-50k.json se for usar a config "modified".

    2. Rodar o treino escolhendo a config:

           python dpr.py --run baseline
           python dpr.py --run modified

       Cada execução salva config, log, checkpoints e métricas finais em
       runs/<config>_<timestamp>/.

    3. Comparar execuções já feitas:

           python compare_runs.py

Por que essas mudanças em relação ao script original:
    - O script original treinava diretamente em cima de data-5k.json, que está no
      formato SQuAD (title/paragraphs/qas), não no formato DPR esperado pelo
      treinador (question/positive_ctxs/hard_negative_ctxs) — o treino não
      aprendia nada (ver dpr.ipynb: loss 0.0000).
    - O script original também usava train_filename == dev_filename == test_filename,
      com um TODO no código pedindo para separar os conjuntos.
    - ElasticsearchDocumentStore exigia subir um container Docker à parte. Trocado
      por um treinador próprio em torch/transformers, sem serviço externo.
"""

import argparse
import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

RUNS_DIR = Path(__file__).parent / "runs"

# baseline = reproduz o comportamento original do repositório (encoder em inglês,
# dataset pequeno), agora treinando de fato no formato DPR correto.
# modified = variação para comparação: encoder pré-treinado em português (BERTimbau),
# dataset maior, mais épocas e mais negativos difíceis por exemplo.
CONFIGS = {
    "baseline": {
        "description": (
            "Reprodução do config original do repositório: bert-base-uncased "
            "(inglês) para query e passage, dataset pequeno (5k), 1 época."
        ),
        "train_filename": "data-5k-dpr.train.json",
        "dev_filename": "data-5k-dpr.dev.json",
        "test_filename": "data-5k-dpr.test.json",
        "query_model": "bert-base-uncased",
        "passage_model": "bert-base-uncased",
        "max_seq_len_query": 64,
        "max_seq_len_passage": 256,
        "n_epochs": 1,
        "batch_size": 16,
        "grad_acc_steps": 8,
        "learning_rate": 1e-5,
        "evaluate_every": 10,
        "embed_title": True,
        "num_hard_negatives": 1,
    },
    "modified": {
        "description": (
            "Encoder pré-treinado em português (BERTimbau) no dataset maior (50k), "
            "com mais épocas e mais negativos difíceis por exemplo."
        ),
        "train_filename": "data-50k-dpr.train.json",
        "dev_filename": "data-50k-dpr.dev.json",
        "test_filename": "data-50k-dpr.test.json",
        "query_model": "neuralmind/bert-base-portuguese-cased",
        "passage_model": "neuralmind/bert-base-portuguese-cased",
        "max_seq_len_query": 64,
        "max_seq_len_passage": 256,
        "n_epochs": 3,
        "batch_size": 8,
        "grad_acc_steps": 16,
        "learning_rate": 1e-5,
        "evaluate_every": 100,
        "embed_title": True,
        "num_hard_negatives": 2,
    },
}


@dataclass
class DPRExample:
    question: str
    positive: str
    hard_negatives: List[str]


def _ctx_text(title: str, text: str, embed_title: bool) -> str:
    return f"{title} {text}" if embed_title and title else text


def load_examples(path: Path, num_hard_negatives: int, embed_title: bool) -> List[DPRExample]:
    with open(path, encoding="utf-8") as f:
        raw_examples = json.load(f)

    examples = []
    for ex in raw_examples:
        if not ex["positive_ctxs"] or not ex["hard_negative_ctxs"]:
            continue
        positive = _ctx_text(ex["positive_ctxs"][0]["title"], ex["positive_ctxs"][0]["text"], embed_title)
        hard_negatives = [
            _ctx_text(ctx["title"], ctx["text"], embed_title) for ctx in ex["hard_negative_ctxs"][:num_hard_negatives]
        ]
        examples.append(DPRExample(question=ex["question"], positive=positive, hard_negatives=hard_negatives))
    return examples


class DPRDataset(Dataset):
    def __init__(self, examples: List[DPRExample]):
        self.examples = examples

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return self.examples[idx]


def collate_fn(batch: List[DPRExample]):
    questions = [ex.question for ex in batch]
    ctxs: List[str] = []
    target_idx: List[int] = []
    for ex in batch:
        target_idx.append(len(ctxs))
        ctxs.append(ex.positive)
        ctxs.extend(ex.hard_negatives)
    return questions, ctxs, torch.tensor(target_idx, dtype=torch.long)


class Biencoder:
    """Dois encoders BERT-like independentes (query e passage). O embedding de
    cada texto é a representação do token [CLS] (last_hidden_state[:, 0])."""

    def __init__(self, query_model: str, passage_model: str, device: torch.device):
        self.device = device
        self.query_tokenizer = AutoTokenizer.from_pretrained(query_model)
        self.passage_tokenizer = AutoTokenizer.from_pretrained(passage_model)
        self.query_encoder = AutoModel.from_pretrained(query_model).to(device)
        self.passage_encoder = AutoModel.from_pretrained(passage_model).to(device)

    def encode_queries(self, texts: List[str], max_len: int) -> torch.Tensor:
        return self._encode(self.query_encoder, self.query_tokenizer, texts, max_len)

    def encode_passages(self, texts: List[str], max_len: int) -> torch.Tensor:
        return self._encode(self.passage_encoder, self.passage_tokenizer, texts, max_len)

    def _encode(self, encoder, tokenizer, texts: List[str], max_len: int) -> torch.Tensor:
        tokens = tokenizer(
            texts, padding=True, truncation=True, max_length=max_len, return_tensors="pt"
        ).to(self.device)
        output = encoder(**tokens)
        return output.last_hidden_state[:, 0]

    def train(self):
        self.query_encoder.train()
        self.passage_encoder.train()

    def eval(self):
        self.query_encoder.eval()
        self.passage_encoder.eval()

    def parameters(self):
        return list(self.query_encoder.parameters()) + list(self.passage_encoder.parameters())

    def save(self, save_dir: Path):
        (save_dir / "query_encoder").mkdir(parents=True, exist_ok=True)
        (save_dir / "passage_encoder").mkdir(parents=True, exist_ok=True)
        self.query_encoder.save_pretrained(save_dir / "query_encoder")
        self.query_tokenizer.save_pretrained(save_dir / "query_encoder")
        self.passage_encoder.save_pretrained(save_dir / "passage_encoder")
        self.passage_tokenizer.save_pretrained(save_dir / "passage_encoder")


def dpr_loss_and_accuracy(biencoder: Biencoder, questions, ctxs, target_idx, config, device):
    query_emb = biencoder.encode_queries(questions, config["max_seq_len_query"])
    ctx_emb = biencoder.encode_passages(ctxs, config["max_seq_len_passage"])
    scores = query_emb @ ctx_emb.T  # (n_questions, n_ctxs) — dot product
    target_idx = target_idx.to(device)
    loss = F.cross_entropy(scores, target_idx)
    accuracy = (scores.argmax(dim=1) == target_idx).float().mean().item()
    return loss, accuracy


@torch.no_grad()
def evaluate(biencoder: Biencoder, loader: DataLoader, config, device) -> dict:
    biencoder.eval()
    total_loss, total_acc, n_batches = 0.0, 0.0, 0
    for questions, ctxs, target_idx in loader:
        loss, accuracy = dpr_loss_and_accuracy(biencoder, questions, ctxs, target_idx, config, device)
        total_loss += loss.item()
        total_acc += accuracy
        n_batches += 1
    biencoder.train()
    if n_batches == 0:
        return {"loss": None, "accuracy": None}
    return {"loss": total_loss / n_batches, "accuracy": total_acc / n_batches}


def run(config_name: str, data_dir: str, seed: int = 42) -> Path:
    config = CONFIGS[config_name]
    random.seed(seed)
    torch.manual_seed(seed)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = RUNS_DIR / f"{config_name}_{timestamp}"
    save_dir = run_dir / "model"
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "config.json").write_text(
        json.dumps({"run": config_name, "timestamp": timestamp, **config}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    logging.basicConfig(format="%(asctime)s %(levelname)s - %(message)s", level=logging.INFO)
    file_handler = logging.FileHandler(run_dir / "train.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(file_handler)

    logging.info("Iniciando run '%s': %s", config_name, config["description"])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info("Usando device: %s", device)

    data_dir = Path(data_dir)
    train_examples = load_examples(data_dir / config["train_filename"], config["num_hard_negatives"], config["embed_title"])
    dev_examples = load_examples(data_dir / config["dev_filename"], config["num_hard_negatives"], config["embed_title"])
    test_examples = load_examples(data_dir / config["test_filename"], config["num_hard_negatives"], config["embed_title"])
    logging.info("Exemplos: train=%s dev=%s test=%s", len(train_examples), len(dev_examples), len(test_examples))

    train_loader = DataLoader(DPRDataset(train_examples), batch_size=config["batch_size"], shuffle=True, collate_fn=collate_fn)
    dev_loader = DataLoader(DPRDataset(dev_examples), batch_size=config["batch_size"], shuffle=False, collate_fn=collate_fn)
    test_loader = DataLoader(DPRDataset(test_examples), batch_size=config["batch_size"], shuffle=False, collate_fn=collate_fn)

    biencoder = Biencoder(config["query_model"], config["passage_model"], device)
    biencoder.train()
    optimizer = torch.optim.AdamW(biencoder.parameters(), lr=config["learning_rate"])

    global_step = 0
    for epoch in range(config["n_epochs"]):
        optimizer.zero_grad()
        for step, (questions, ctxs, target_idx) in enumerate(train_loader):
            loss, accuracy = dpr_loss_and_accuracy(biencoder, questions, ctxs, target_idx, config, device)
            (loss / config["grad_acc_steps"]).backward()

            if (step + 1) % config["grad_acc_steps"] == 0:
                optimizer.step()
                optimizer.zero_grad()
                global_step += 1

                if global_step % config["evaluate_every"] == 0:
                    dev_metrics = evaluate(biencoder, dev_loader, config, device)
                    logging.info(
                        "epoch=%s step=%s train_loss=%.4f train_acc=%.4f dev_loss=%s dev_acc=%s",
                        epoch, global_step, loss.item(), accuracy, dev_metrics["loss"], dev_metrics["accuracy"],
                    )

        logging.info("Fim da época %s/%s", epoch + 1, config["n_epochs"])

    dev_metrics = evaluate(biencoder, dev_loader, config, device)
    test_metrics = evaluate(biencoder, test_loader, config, device)
    logging.info("Métricas finais — dev: %s | test: %s", dev_metrics, test_metrics)

    biencoder.save(save_dir)
    (run_dir / "results.json").write_text(
        json.dumps({"dev": dev_metrics, "test": test_metrics}, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    logging.info("Run '%s' finalizada. Modelo salvo em %s", config_name, save_dir)
    print(f"Run '{config_name}' concluída. Artefatos em: {run_dir}")
    return run_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Treina o DPR usando a config baseline ou modified.")
    parser.add_argument("--run", choices=list(CONFIGS), default="baseline", help="Qual config rodar.")
    parser.add_argument(
        "--data-dir",
        default=".",
        help="Diretório com os arquivos *-dpr.train/dev/test.json gerados pelo squad_to_dpr.py.",
    )
    args = parser.parse_args()
    run(args.run, args.data_dir)
