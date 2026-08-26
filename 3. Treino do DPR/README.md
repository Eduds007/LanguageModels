# DPR Training

Training pipeline for a Portuguese DPR (Dense Passage Retriever): two BERT-like
encoders (query and passage) trained to bring the correct question and passage
close together in embedding space, using an NLL loss over the positive + hard
negatives + "in-batch" negatives (same formulation as the original paper,
Karpukhin et al., 2020).

> **This project is about two years old.** It was built at a time when
> Portuguese language models (and available encoders in general) were much
> more limited than today's. The numbers below reflect that context — nowadays
> you'd likely get much better results by swapping in more recent base
> encoders.

## How to run

```bash
cd "3. Treino do DPR"
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

1. Convert the SQuAD-like dataset to DPR format (mines hard negatives locally
   with TF-IDF, no need for Elasticsearch/Haystack):

   ```bash
   python squad_to_dpr.py --squad_input_filename data-5k.json \
       --dpr_output_filename data-5k-dpr.json --split_dataset
   ```

2. Train, picking a config:

   ```bash
   python dpr.py --run baseline    # bert-base-uncased, 5k dataset, 1 epoch
   python dpr.py --run modified    # BERTimbau, 50k dataset, 3 epochs
   ```

   Each run saves its config, log, and checkpoints to `runs/<config>_<timestamp>/`.

3. Compare runs already done:

   ```bash
   python compare_runs.py
   ```

4. (Optional) Serve real retrieval with a trained checkpoint — see
   `../dpr_service.py` at the project root, which loads the saved encoders and
   indexes the passages to answer queries via an API.

## Accuracy

Both configs use the same metric — top-1 accuracy: given a batch, the model
has to point to which of the candidate passages in the batch is the correct
answer for each question (positive + hard negatives + "in-batch" negatives
from other questions in the same batch).

| Run | Encoder | Dataset | Epochs | Dev accuracy | Test accuracy |
|---|---|---|---|---|---|
| `baseline` | bert-base-uncased (English) | 5k, batch 16 | 1 | 40.0% | 36.9% |
| `modified` | BERTimbau (Portuguese) | 50k, batch 8 | 3 | 88.5% | 89.5% |

Chance level is ~3% for `baseline` (batch size 16 × 2 passages/question ≈ 32
candidates) and ~2% for `modified` (batch size 8 × 3 candidates ≈ 24). The
jump from `baseline` to `modified` comes mostly from swapping the English
encoder for a Portuguese-pretrained one, plus more training data/epochs.

## Exemplos de retrieval real (50k passagens)

A métrica de accuracy acima só compara a passagem certa contra ~24 candidatos
por batch (positivo + negativos difíceis + in-batch). Para dar uma ideia de
qualidade "no mundo real", seguem exemplos rodando `../dpr_service.py` (com
o checkpoint `modified`, BERTimbau treinado no `data-50k.json`) contra o
índice completo das 49.435 passagens — aqui a passagem certa precisa vencer
todas as outras do corpus, não só as ~24 do batch.

| Pergunta | Artigo esperado | Top-1 retornado | Score | Acerto |
|---|---|---|---|---|
| homem formiga e a vespa dc ou maravilha | O Homem e a Vespa | O Homem e a Vespa | 54.28 | ✅ |
| Quantas nações fazem parte das nações unidas | Estados-membros das Nações Unidas | Comunidade das Nações | 56.73 | ❌ |
| quem marcou mais corridas em odi | Lista de recordes de críquete ODI | Lista de recordes de pilotos de Fórmula 1 | 53.45 | ❌ |
| Quando saiu o primeiro filme de punição | O Justiceiro (1989) | Psycho (filme de 1960) | 53.09 | ❌ |
| O que significa se o wronskian é zero? | Wronskian | Wronskian | 61.11 | ✅ |
| Onde foi filmado o início da Mulher Maravilha | Mulher Maravilha (filme de 2017) | Mulher Maravilha (filme de 2017) | 55.04 | ✅ |
| quem joga poussey washington em laranja é o novo preto | Laranja é o novo preto | Laranja é o novo preto | 59.75 | ✅ |
| quem teve mais vitórias na nfl | (recordes de vitórias na NFL) | NCAA division i FBS football win - recordes de derrotas | 56.87 | ❌ |

4/8 acertos de artigo no top-1 nesta amostra — bem abaixo dos ~89% medidos em
batch, o que é esperado dado o salto de ~24 para 49.435 candidatos. Os erros
seguem um padrão: o retriever acerta o tema (esporte, cinema) mas erra o
artigo específico quando há vários artigos parecidos no corpus.

## Limitations / history

The `modified` config (BERTimbau + 50k dataset + more epochs) **was not
completed for a long time** — the hardware available during earlier
development (a CPU that was unstable under sustained load) caused recurring
crashes and, in one case, froze the machine entirely, preventing this larger
training run from finishing.

It has since been run to completion on a machine with a GPU (RTX 4090) — see
the `modified` row in [Accuracy](#accuracy) above and the retrieval examples
below. Training took about 25 minutes end-to-end (data conversion + 3
epochs). Anyone wanting to improve further (more modern encoders, more hard
negatives, full-corpus/FAISS-based negative mining instead of TF-IDF) is
welcome to build on top of this run.
