"""
Script to convert a SQuAD-like QA-dataset format JSON file to DPR Dense Retriever training format.

Não depende de Elasticsearch/FAISS/Haystack: a mineração de negativos difíceis é
feita localmente com um retriever TF-IDF (scikit-learn) sobre os próprios parágrafos
do dataset — suficiente para achar candidatos textualmente parecidos com a pergunta
que não contêm a resposta certa.

Usage:
    squad_to_dpr.py --squad_input_filename <squad_input_filename> --dpr_output_filename <dpr_output_filename> [options]
Arguments:
    --num_hard_negative_ctxs HNEG       Number of hard negative contexts [default: 30]
    --split_dataset                     Whether to split the created dataset or not [default: False]

SQuAD format
{
    version: "Version du dataset"
    data:[
            {
                title: "Titre de l'article Wikipedia"
                paragraphs:[
                    {
                        context: "Paragraph de l'article"
                        qas:[
                            {
                                id: "Id du pair question-réponse"
                                question: "Question"
                                answers:[
                                    {
                                        "answer_start": "Position de la réponse"
                                        "text": "Réponse"
                                    }
                                ],
                                is_impossible: (not in v1)
                            }
                        ]
                    }
                ]
            }
    ]
}


DPR format
[
    {
        "question": "....",
        "answers": ["...", "...", "..."],
        "positive_ctxs": [{
            "title": "...",
            "text": "...."
        }],
        "negative_ctxs": ["..."],
        "hard_negative_ctxs": ["..."]
    },
    ...
]
"""

import argparse
import json
import logging
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import Iterator, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

logger = logging.getLogger(__name__)


@dataclass
class Passage:
    title: str
    text: str


class TfidfHardNegativeMiner:
    """Indexa os parágrafos do próprio dataset com TF-IDF e recupera, para cada
    pergunta, os parágrafos textualmente mais parecidos — candidatos a negativo
    difícil (o filtro por resposta é feito depois, em get_hard_negative_contexts)."""

    def __init__(self, passages: List[Passage]):
        self.passages = passages
        self.vectorizer = TfidfVectorizer(lowercase=True)
        self.matrix = self.vectorizer.fit_transform(p.text for p in passages)

    def retrieve(self, query: str, top_k: int) -> List[Passage]:
        query_vec = self.vectorizer.transform([query])
        scores = np.asarray((self.matrix @ query_vec.T).todense()).ravel()
        top_idx = np.argsort(-scores)[:top_k]
        return [self.passages[i] for i in top_idx]


def add_is_impossible(squad_data: dict, json_file_path: Path):
    new_path = json_file_path.parent / Path(f"{json_file_path.stem}_impossible.json")
    for article in squad_data["data"]:
        for paragraph in article["paragraphs"]:
            for question in paragraph["qas"]:
                question["is_impossible"] = False

    with open(new_path, "w", encoding="utf-8") as filo:
        json.dump(squad_data, filo, indent=4, ensure_ascii=False)

    return new_path, squad_data


def get_number_of_questions(squad_data: list):
    return sum(len(paragraph["qas"]) for article in squad_data for paragraph in article["paragraphs"])


def has_is_impossible(squad_data: dict):
    for article in squad_data["data"]:
        for paragraph in article["paragraphs"]:
            for question in paragraph["qas"]:
                if "is_impossible" in question:
                    return True
    return False


def collect_passages(squad_data: list) -> List[Passage]:
    return [
        Passage(title=article.get("title", ""), text=paragraph["context"])
        for article in squad_data
        for paragraph in article["paragraphs"]
    ]


def get_hard_negative_contexts(miner: TfidfHardNegativeMiner, question: str, answers: List[str], n_ctxs: int = 30):
    # busca uma margem maior que n_ctxs pois parte dos candidatos será descartada
    # por conter a resposta certa (não seria um negativo de verdade)
    candidates = miner.retrieve(query=question, top_k=n_ctxs * 3 + 10)
    hard_negative_ctxs = []
    for passage in candidates:
        if any(str(answer).lower() in passage.text.lower() for answer in answers):
            continue
        hard_negative_ctxs.append({"title": passage.title, "text": passage.text, "passage_id": ""})
        if len(hard_negative_ctxs) >= n_ctxs:
            break
    return hard_negative_ctxs


def create_dpr_training_dataset(squad_data: list, miner: TfidfHardNegativeMiner, num_hard_negative_ctxs: int = 30):
    n_non_added_questions = 0
    n_questions = 0
    for article in tqdm(squad_data, unit="article"):
        article_title = article.get("title", "")
        for paragraph in article["paragraphs"]:
            context = paragraph["context"]
            for question in paragraph["qas"]:
                if "is_impossible" in question and question["is_impossible"]:
                    continue
                answers = [a["text"] for a in question["answers"]]
                hard_negative_ctxs = get_hard_negative_contexts(
                    miner=miner, question=question["question"], answers=answers, n_ctxs=num_hard_negative_ctxs
                )
                positive_ctxs = [{"title": article_title, "text": context, "passage_id": ""}]

                if not hard_negative_ctxs or not positive_ctxs:
                    logger.error(
                        "No retrieved candidates for article %s, with question %s", article_title, question["question"]
                    )
                    n_non_added_questions += 1
                    continue
                dict_DPR = {
                    "question": question["question"],
                    "answers": answers,
                    "positive_ctxs": positive_ctxs,
                    "negative_ctxs": [],
                    "hard_negative_ctxs": hard_negative_ctxs,
                }
                n_questions += 1
                yield dict_DPR

    logger.info("Number of skipped questions: %s", n_non_added_questions)
    logger.info("Number of added questions: %s", n_questions)


def save_dataset(iter_dpr: Iterator, dpr_output_filename: Path, total_nb_questions: int, split_dataset: bool):
    if split_dataset:
        nb_train_examples = int(total_nb_questions * 0.8)
        nb_dev_examples = int(total_nb_questions * 0.1)

        train_iter = islice(iter_dpr, nb_train_examples)
        dev_iter = islice(iter_dpr, nb_dev_examples)

        dataset_splits = {
            dpr_output_filename.parent / f"{dpr_output_filename.stem}.train.json": train_iter,
            dpr_output_filename.parent / f"{dpr_output_filename.stem}.dev.json": dev_iter,
            dpr_output_filename.parent / f"{dpr_output_filename.stem}.test.json": iter_dpr,
        }
    else:
        dataset_splits = {dpr_output_filename: iter_dpr}
    for path, set_iter in dataset_splits.items():
        examples = list(set_iter)
        with open(path, "w", encoding="utf-8") as json_ds:
            json.dump(examples, json_ds, indent=4, ensure_ascii=False)
        logger.info("Salvo %s (%s exemplos)", path, len(examples))


def load_squad_file(squad_file_path: Path):
    if not squad_file_path.exists():
        raise FileNotFoundError(squad_file_path)

    with open(squad_file_path, encoding="utf-8") as squad_file:
        squad_data = json.load(squad_file)

    if not has_is_impossible(squad_data=squad_data):
        squad_file_path, squad_data = add_is_impossible(squad_data, squad_file_path)

    return squad_file_path, squad_data["data"]


def main(
    squad_input_filename: Path,
    dpr_output_filename: Path,
    num_hard_negative_ctxs: int = 30,
    split_dataset: bool = True,
):
    tqdm.write(f"Using SQuAD-like file {squad_input_filename}")

    _, squad_data = load_squad_file(squad_file_path=squad_input_filename)

    passages = collect_passages(squad_data)
    logger.info("Indexando %s parágrafos com TF-IDF para mineração de negativos difíceis...", len(passages))
    miner = TfidfHardNegativeMiner(passages)

    iter_DPR = create_dpr_training_dataset(
        squad_data=squad_data, miner=miner, num_hard_negative_ctxs=num_hard_negative_ctxs
    )

    total_nb_questions = get_number_of_questions(squad_data)
    save_dataset(
        iter_dpr=iter_DPR,
        dpr_output_filename=dpr_output_filename,
        total_nb_questions=total_nb_questions,
        split_dataset=split_dataset,
    )


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.INFO)

    parser = argparse.ArgumentParser(description="Convert a SQuAD JSON format dataset to DPR format.")
    parser.add_argument(
        "--squad_input_filename",
        dest="squad_input_filename",
        help="A dataset with a SQuAD JSON format.",
        metavar="SQUAD_in",
        required=True,
    )
    parser.add_argument(
        "--dpr_output_filename",
        dest="dpr_output_filename",
        help="The name of the DPR JSON formatted output file",
        metavar="DPR_out",
        required=True,
    )
    parser.add_argument(
        "--num_hard_negative_ctxs",
        dest="num_hard_negative_ctxs",
        help="Number of hard negative contexts to use",
        metavar="num_hard_negative_ctxs",
        type=int,
        default=30,
    )
    parser.add_argument(
        "--split_dataset",
        dest="split_dataset",
        action="store_true",
        help="Whether to split the created dataset or not (default: False)",
    )

    args = parser.parse_args()

    main(
        squad_input_filename=Path(args.squad_input_filename),
        dpr_output_filename=Path(args.dpr_output_filename),
        num_hard_negative_ctxs=args.num_hard_negative_ctxs,
        split_dataset=args.split_dataset,
    )
